"""Run with Python; Lua tests require lupa (install in .test-deps or environment)."""
from pathlib import Path
import json, os, re, sqlite3, sys, unittest, zlib, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(os.environ.get('CIV6_GAME_DIR','E:/Games/Sid Meiers Civilization VI Rulers of England'))
sys.path.insert(0, str(ROOT/'.test-deps'))
from lupa import LuaRuntime

def lua_runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
        callbacks = {}
        Events = setmetatable({}, {__index=function(t,k)
            local event={Add=function(fn) callbacks[k]=fn end}; rawset(t,k,event); return event
        end})
        function include() end
        function print() end
    ''')
    return lua

class ManifestTests(unittest.TestCase):
    def test_manifest_files_and_dependencies(self):
        root=ET.parse(ROOT/'UltimateExperience.modinfo').getroot()
        self.assertEqual(len(root.findall('Dependencies/Mod')),7)
        for f in root.findall('Files/File'): self.assertTrue((ROOT/f.text).is_file(),f.text)
        for p in ROOT.rglob('*.xml'):
            if '.test-deps' not in p.parts: ET.parse(p)
        actions=root.find('InGameActions')
        orders={n.get('id'):n.findtext('Properties/LoadOrder') for n in actions}
        self.assertEqual(orders['UE_Capture'],'4')
        self.assertEqual(orders['UE_Restore'],'8')
    def test_lua_syntax(self):
        lua=lua_runtime()
        for folder in ['Gameplay','UI']:
            for file in (ROOT/folder).glob('*.lua'):
                lua.execute('assert(load(...))',file.read_text(encoding='utf-8'))
    def test_ui_wrappers_are_available_without_shadowing(self):
        manifest=ET.parse(ROOT/'UltimateExperience.modinfo').getroot()
        contexts=[n.findtext('Properties/LuaContext') for n in manifest.findall('InGameActions/ReplaceUIScript')]
        self.assertNotIn('ProductionPanel',contexts)
        self.assertFalse((ROOT/'UI/TopPanel.lua').exists())
        imported=set()
        upstream_names=set()
        for folder in ROOT.parent.iterdir():
            if not folder.is_dir() or folder==ROOT: continue
            for info in folder.glob('*.modinfo'):
                tree=ET.parse(info).getroot()
                imported.update(Path(f.text).stem.lower() for action in tree.iter('ImportFiles') for f in action.iter('File'))
            upstream_names.update(p.name.lower() for p in folder.rglob('*.lua'))
        for f in (ROOT/'UI').glob('*.lua'):
            self.assertNotIn(f.name.lower(),upstream_names)
            for name in re.findall(r"include\(['\"]([^'\"]+)['\"]\)",f.read_text()):
                self.assertIn(name.lower(),imported,'Dependency must import include target: '+name)

class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file=Path.home()/'AppData/Local/Firaxis Games'/"Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
        if not file.is_file() or not (GAME/'DLC/Expansion1').is_dir() or not (ROOT.parent/"2542898147 Sukritact's Oceans").is_dir():
            raise unittest.SkipTest('Local Civ VI cache, game assets and sibling dependency mods required')
        cls.source=sqlite3.connect(file.as_uri()+'?mode=ro',uri=True)
    @classmethod
    def tearDownClass(cls): cls.source.close()
    def setUp(self):
        self.db=sqlite3.connect(':memory:'); self.source.backup(self.db)
        # Firaxis registers this SQL helper in-process. Hash values are not part
        # of the balance comparison; use deterministic unique test values.
        self.db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
        # The main menu replaces DebugGameplay with the base-rules database.
        # Load the real GS table declaration if this cache is from the menu.
        if not self.db.execute("SELECT 1 FROM sqlite_master WHERE name='Project_ResourceCosts'").fetchone():
            schema=(GAME/'DLC/Expansion2/Data/Expansion2_Schema.sql').read_text(encoding='utf-8-sig')
            statement=re.search(r'CREATE TABLE "Project_ResourceCosts"\s*\([\s\S]*?;',schema).group(0)
            self.db.executescript(statement)
        # Populate the affected expansion rows from installed official XML when
        # testing against the menu cache. Do not pretend it is a running GS save.
        if not self.db.execute("SELECT 1 FROM Improvements WHERE ImprovementType='IMPROVEMENT_FISHERY'").fetchone():
            expansion=GAME/'DLC/Expansion1/Data'
            wanted={'IMPROVEMENT_FISHERY','Fishery_SeaResourceAdjacency','BUILDING_AQUARIUM','BUILDING_AQUATICS_CENTER','AQUARIUM_SEARESOURCE_SCIENCE','AQUARIUM_REEF_SCIENCE','AQUATICS_CENTER_WONDER_TOURISM'}
            for file in [expansion/'Expansion1_Improvements.xml',expansion/'Expansion1_Buildings.xml']:
                for table in ET.parse(file).getroot():
                    for row in table.findall('Row'):
                        data=dict(row.attrib);data.update({child.tag:child.text for child in row})
                        if not wanted.intersection(data.values()): continue
                        if not self.db.execute('SELECT 1 FROM sqlite_master WHERE type="table" AND name=?',(table.tag,)).fetchone(): continue
                        columns={c[1] for c in self.db.execute('PRAGMA table_info('+table.tag+')')}
                        data={k:(1 if v.lower()=='true' else 0 if v.lower()=='false' else v) for k,v in data.items() if k in columns}
                        self.db.execute('INSERT OR IGNORE INTO '+table.tag+' ('+','.join('"'+k+'"' for k in data)+') VALUES ('+','.join('?' for _ in data)+')',list(data.values()))
            self.db.commit()
    def tearDown(self): self.db.close()
    def run_sql(self,path): self.db.executescript(path.read_text(encoding='utf-8-sig'))
    def test_oceans_preserves_existing_rules(self):
        if self.db.execute("SELECT 1 FROM Features WHERE FeatureType='FEATURE_SUK_KELP'").fetchone():
            self.skipTest('Replay requires a pre-Oceans cache; current cache is the campaign')
        tables=['Improvements','Improvement_Adjacencies','Improvement_YieldChanges','ImprovementModifiers','BuildingModifiers','DistrictModifiers','Features','Resources','Resource_ValidTerrains','Resource_ValidFeatures']
        before={t:set(self.db.execute('SELECT * FROM '+t)) for t in tables}
        self.assertFalse(self.db.execute("SELECT 1 FROM Features WHERE FeatureType='FEATURE_SUK_KELP'").fetchone(), 'Need a baseline without Oceans')
        self.run_sql(ROOT/'Data/OceansCapture.sql')
        ocean=ROOT.parent/"2542898147 Sukritact's Oceans/Core"
        for name in ['Features','Improvements','Resources','Buildings']: self.run_sql(ocean/('Suk_Oceans_'+name+'.sql'))
        self.run_sql(ROOT/'Data/OceansRestore.sql')
        for table in tables:
            after=set(self.db.execute('SELECT * FROM '+table))
            self.assertFalse(before[table]-after, 'Existing rows changed in '+table+': '+str(before[table]-after)[:500])
        for table in ['Improvement_Adjacencies','Improvement_YieldChanges','ImprovementModifiers','BuildingModifiers','DistrictModifiers']:
            self.assertEqual(before[table],set(self.db.execute('SELECT * FROM '+table)),table)
        self.assertEqual(self.db.execute("SELECT count(*) FROM Resources WHERE ResourceType LIKE 'RESOURCE_SUK_%'").fetchone()[0],7)
        self.assertTrue(self.db.execute("SELECT Workable FROM Improvements WHERE ImprovementType='IMPROVEMENT_FISHERY'").fetchone()[0])
        self.assertFalse(self.db.execute("SELECT name FROM sqlite_master WHERE name LIKE 'UE_Original%'").fetchall())
        self.assertTrue(self.db.execute("SELECT 1 FROM Improvement_ValidResources WHERE ResourceType='RESOURCE_SUK_SQUID'").fetchone())
    def test_bbg_fishery_rules_win_after_oceans(self):
        if self.db.execute("SELECT 1 FROM Features WHERE FeatureType='FEATURE_SUK_KELP'").fetchone():
            self.skipTest('BBG-only comparison requires a pre-Oceans cache')
        # An existing game cache may already contain this BBG section. Remove
        # only its generated rows so replaying the real script is meaningful.
        for table,column,values in [
            ('BuildingModifiers','ModifierId',['BBG_SHIPYARD_FISHERY_PRODUCTION']),
            ('ModifierArguments','ModifierId',['BBG_SHIPYARD_FISHERY_PRODUCTION']),
            ('Modifiers','ModifierId',['BBG_SHIPYARD_FISHERY_PRODUCTION']),
            ('RequirementSetRequirements','RequirementSetId',['BBG_TILE_IS_FISHERY_REQSET']),
            ('RequirementSets','RequirementSetId',['BBG_TILE_IS_FISHERY_REQSET']),
            ('RequirementArguments','RequirementId',['BBG_TILE_IS_FISHERY_REQUIREMENT']),
            ('Requirements','RequirementId',['BBG_TILE_IS_FISHERY_REQUIREMENT'])]:
            self.db.execute('DELETE FROM '+table+' WHERE '+column+'=?',values)
        self.db.commit()
        plain=sqlite3.connect(':memory:');self.db.backup(plain)
        plain.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
        script=(ROOT.parent/'BBG/sql/XP2/Governors.sql').read_text(encoding='utf-8-sig').split('-- Fishery moved to tech tree',1)[1]
        base=(ROOT.parent/'BBG/sql/Base/base.sql').read_text(encoding='utf-8-sig')
        housing=re.search(r"UPDATE Improvements SET Housing=2 WHERE ImprovementType='IMPROVEMENT_FISHERY';",base).group(0)
        plain.executescript(housing+script)
        self.run_sql(ROOT/'Data/OceansCapture.sql')
        for name in ['Features','Improvements','Resources','Buildings']:
            self.run_sql(ROOT.parent/"2542898147 Sukritact's Oceans/Core"/('Suk_Oceans_'+name+'.sql'))
        self.run_sql(ROOT/'Data/OceansRestore.sql')
        self.db.executescript(housing+script)
        for table,where in [('Improvements',"ImprovementType='IMPROVEMENT_FISHERY'"),('Improvement_YieldChanges',"ImprovementType='IMPROVEMENT_FISHERY'"),('Improvement_Adjacencies',"ImprovementType='IMPROVEMENT_FISHERY'"),('ImprovementModifiers',"ImprovementType='IMPROVEMENT_FISHERY'"),('BuildingModifiers',"BuildingType='BUILDING_SHIPYARD'")]:
            query='SELECT * FROM '+table+' WHERE '+where
            self.assertEqual(set(self.db.execute(query)),set(plain.execute(query)),table)
        self.assertEqual(self.db.execute("SELECT PrereqTech, TraitType, Housing, Workable FROM Improvements WHERE ImprovementType='IMPROVEMENT_FISHERY'").fetchone(),('TECH_CELESTIAL_NAVIGATION',None,2,1))
        plain.close()
    def test_reconstruction_schema_and_human_unlock(self):
        prior=set(self.db.execute('PRAGMA foreign_key_check'))
        if not self.db.execute("SELECT 1 FROM Projects WHERE ProjectType='PROJECT_UE_RECONSTRUCTION'").fetchone():
            self.run_sql(ROOT/'Data/Reconstruction.sql')
        self.assertEqual(self.db.execute("SELECT StartProductionCost FROM Project_ResourceCosts WHERE ProjectType='PROJECT_UE_RECONSTRUCTION'").fetchone(),(2,))
        self.assertEqual(self.db.execute("SELECT UnlocksFromEffect FROM Projects WHERE ProjectType='PROJECT_UE_RECONSTRUCTION'").fetchone(),(1,))
        self.assertEqual(self.db.execute("SELECT RequirementType FROM Requirements WHERE RequirementId='UE_IS_HUMAN'").fetchone(),('REQUIREMENT_PLAYER_IS_HUMAN',))
        self.assertFalse(set(self.db.execute('PRAGMA foreign_key_check'))-prior)
    def test_localization_roundtrip(self):
        db=sqlite3.connect(':memory:')
        db.execute('CREATE TABLE LocalizedText (Tag TEXT, Language TEXT, Text TEXT, PRIMARY KEY(Tag,Language))')
        db.execute("INSERT INTO LocalizedText VALUES ('LOC_IMPROVEMENT_FISHERY_DESCRIPTION','en_US','BBG original')")
        db.executescript((ROOT/'Text/OceansCapture.sql').read_text())
        db.execute("UPDATE LocalizedText SET Text='Oceans replacement'")
        db.executescript((ROOT/'Text/OceansRestore.sql').read_text())
        self.assertEqual(db.execute("SELECT Text FROM LocalizedText WHERE Tag='LOC_IMPROVEMENT_FISHERY_DESCRIPTION'").fetchone(),('BBG original',))
        db.close()

    def test_bbm_registers_oceans_resources(self):
        source=ROOT.parent/'3179425402 Better Balanced Maps 1.37/Data/BBS Maps/Utility/BBS_ResourceGenerator.lua'
        if not source.exists(): self.skipTest('Installed BBM 1.37 required')
        if not self.db.execute("SELECT 1 FROM Resources WHERE ResourceType='RESOURCE_SUK_SQUID'").fetchone():
            self.run_sql(ROOT.parent/"2542898147 Sukritact's Oceans/Core/Suk_Oceans_Resources.sql")
        # Execute BBM's real registration method with the combined database.
        script=source.read_text(encoding='utf-8-sig')
        method=script.split('function BBS_ResourceGenerator:__InitResourceData()',1)[1].split('function BBS_ResourceGenerator:__GetLuxuryResources()',1)[0]
        lua=lua_runtime()
        lua.execute('BBS_ResourceGenerator={};Map={GetMapSize=function() return 0 end};GameInfo={Maps={[0]={DefaultPlayers=6}}}')
        raw=self.db.execute('SELECT ResourceType,ResourceClassType,Frequency,SeaFrequency,PeakEra FROM Resources ORDER BY ResourceType').fetchall()
        # Index and Hash are supplied by GameInfo, not SQLite's Resources table.
        rows=[(r[0],zlib.crc32(r[0].encode()),i,*r[1:]) for i,r in enumerate(raw)]
        lua.globals().rows=lua.table_from([lua.table_from(dict(zip(['ResourceType','Hash','Index','ResourceClassType','Frequency','SeaFrequency','PeakEra'],r))) for r in rows])
        lua.execute('GameInfo.Resources=function() local i=0;return function() i=i+1;return rows[i] end end')
        lua.execute('function BBS_ResourceGenerator:__InitResourceData()'+method)
        lua.execute('''instance={resources=2,iTargetPercentage=30}
          for _,k in ipairs({'eResourceName','eResourceType','aIndex','eResourceClassType','aaPossibleLocs','aaPossibleWaterLocs','aaPossibleLuxLocs','aaPossibleStratLocs','iFrequency','iSeaFrequency','aPeakEra'}) do instance[k]={} end
          BBS_ResourceGenerator.__InitResourceData(instance)''')
        registered={lua.globals().instance.eResourceName[i] for i in range(len(rows))}
        expected={r[0] for r in rows if r[0].startswith('RESOURCE_SUK_')}
        self.assertEqual(len(expected),7)
        self.assertTrue(expected.issubset(registered))

    def test_loaded_oceans_bbg_rules(self):
        if not self.db.execute("SELECT 1 FROM Features WHERE FeatureType='FEATURE_SUK_KELP'").fetchone():
            self.skipTest('Combined campaign cache required')
        self.assertEqual(self.db.execute("SELECT PrereqTech,TraitType,Housing,Workable FROM Improvements WHERE ImprovementType='IMPROVEMENT_FISHERY'").fetchone(),('TECH_CELESTIAL_NAVIGATION',None,2,1))
        self.assertEqual(self.db.execute("SELECT count(*) FROM Resources WHERE ResourceType LIKE 'RESOURCE_SUK_%'").fetchone()[0],7)
        self.assertTrue(self.db.execute("SELECT 1 FROM BuildingModifiers WHERE BuildingType='BUILDING_SHIPYARD' AND ModifierId='BBG_SHIPYARD_FISHERY_PRODUCTION'").fetchone())

class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.lua=lua_runtime()
        self.lua.execute('''
        iron=100; repaired={}; complete=0; human=true; props={}; current=123
        buildingsList={{Index=8},{Index=2},{Index=4}}
        pillagedBuildings={[2]=true,[4]=true,[8]=false}
        district={pillaged=true, GetX=function() return 1 end,GetY=function() return 2 end,
          IsPillaged=function(self) return self.pillaged end,
          SetPillaged=function(self,v) self.pillaged=v; table.insert(repaired,'district') end}
        districts={GetNumDistricts=function() return 1 end, GetDistrictByIndex=function() return district end}
        buildings={HasBuilding=function() return true end,
          IsPillaged=function(self,id) return pillagedBuildings[id] end,
          GetBuildingLocation=function() return 99 end,
          SetPillaged=function(self,id,v) pillagedBuildings[id]=v;table.insert(repaired,id) end}
        queue={GetCurrentProductionTypeHash=function() return current end,
          FinishProgress=function() complete=complete+1;current=0;callbacks.CityProductionChanged(0,1,3,7) end}
        city={GetBuildQueue=function() return queue end, GetDistricts=function() return districts end,
          GetBuildings=function() return buildings end, GetProperty=function(self,k) return props[k] end,
          SetProperty=function(self,k,v) props[k]=v end,GetX=function() return 1 end,GetY=function() return 2 end}
        resources={GetResourceAmount=function() return iron end,ChangeResourceAmount=function(self,id,v) iron=iron+v end}
        Players={[0]={IsHuman=function() return human end,GetResources=function() return resources end}}
        CityManager={GetCity=function() return city end}
        GameInfo={Projects={[7]={ProjectType='PROJECT_UE_RECONSTRUCTION',Hash=123}},Resources={RESOURCE_IRON={Index=1}},
          Buildings=function() local i=0; return function() i=i+1;return buildingsList[i] end end}
        Map={GetPlot=function() return {GetIndex=function() return 99 end} end}
        Game={GetLocalPlayer=function() return 0 end,AddWorldViewText=function() end}
        Locale={Lookup=function() return '' end}
        ''')
        self.lua.execute((ROOT/'Gameplay/Reconstruction.lua').read_text())
    def run_repair(self,iron):
        self.lua.globals().iron=iron
        self.lua.execute('callbacks.CityProductionChanged(0,1,3,7)')
    def test_district_then_sorted_buildings(self):
        self.run_repair(22)
        self.assertEqual(list(self.lua.globals().repaired.values()),['district',2,4])
        self.assertEqual(self.lua.globals().iron,0)
        self.assertEqual(self.lua.globals().complete,1)
    def test_unaffordable_parent_blocks_buildings(self):
        self.run_repair(9)
        self.assertEqual(len(self.lua.globals().repaired),0)
        self.assertEqual(self.lua.globals().iron,9)
    def test_partial_repair(self):
        self.run_repair(16)
        self.assertEqual(list(self.lua.globals().repaired.values()),['district',2])
        self.assertEqual(self.lua.globals().iron,0)
    def test_no_damage_no_extra_cost(self):
        self.lua.execute('district.pillaged=false;pillagedBuildings={}')
        self.run_repair(0)
        self.assertEqual(self.lua.globals().iron,0)
    def test_duplicate_and_reload_do_not_repair_again(self):
        self.run_repair(100)
        self.lua.execute((ROOT/'Gameplay/Reconstruction.lua').read_text())
        self.lua.execute('callbacks.CityProductionChanged(0,1,3,7)')
        self.assertEqual(self.lua.globals().complete,1)
        self.assertEqual(self.lua.globals().iron,78)
    def test_ai_and_unrelated_notifications_ignored(self):
        self.lua.execute('human=false; callbacks.CityProductionChanged(0,1,3,7); callbacks.CityProductionChanged(0,1,2,7)')
        self.assertEqual(self.lua.globals().complete,0)

class ReconTests(unittest.TestCase):
    def setUp(self):
        self.lua=lua_runtime()
        self.lua.execute('''
        points=30; level=1; active=true; barbarian=true; promotion='PROMOTION_CLASS_RECON'; properties={}; awards=0
        CombatResultParameters={ID='id',ATTACKER='attacker',DEFENDER='defender',EXPERIENCE_CHANGE='xp'}
        experience={GetLevel=function() return level end,GetExperiencePoints=function() return points end,
          ChangeExperience=function(self,n) points=points+n;awards=awards+1 end}
        unit={GetExperience=function() return experience end,GetType=function() return 1 end,
          GetProperty=function(self,k) return properties[k] end,SetProperty=function(self,k,v) properties[k]=v end}
        UnitManager={GetUnit=function(player,id) if player==0 then return unit end end}
        Players={[0]={GetCulture=function() return {IsPolicyActive=function() return active end} end,IsBarbarian=function() return false end},
                 [63]={IsBarbarian=function() return barbarian end,GetCulture=function() return {IsPolicyActive=function() return false end} end}}
        GameInfo={Policies={POLICY_SURVEY={Index=1}},Units=setmetatable({}, {__index=function() return {PromotionClass=promotion} end})}
        function combat(xp)
          return {attacker={id={type=1,player=0,id=10},xp=xp},defender={id={type=1,player=63,id=12},xp=0}}
        end
        ''')
        self.lua.execute((ROOT/'Gameplay/ReconXP.lua').read_text())
    def test_reduced_xp_doubled(self):
        self.lua.execute('callbacks.Combat(combat(1))')
        self.assertEqual(self.lua.globals().points,31)
    def test_engine_already_doubled_untouched(self):
        self.lua.execute('callbacks.Combat(combat(2))')
        self.assertEqual(self.lua.globals().awards,0)
    def test_replayed_and_reloaded_event(self):
        self.lua.execute('event=combat(1);callbacks.Combat(event);callbacks.Combat(event);callbacks.Combat(combat(1))')
        self.lua.execute((ROOT/'Gameplay/ReconXP.lua').read_text())
        self.lua.execute('callbacks.Combat(combat(1))')
        self.assertEqual(self.lua.globals().awards,1)
    def test_next_real_combat(self):
        self.lua.execute('callbacks.Combat(combat(1));points=points+1;callbacks.Combat(combat(1))')
        self.assertEqual(self.lua.globals().awards,2)
    def test_ineligible_cases(self):
        for setup in ['level=0','active=false','barbarian=false',"promotion='PROMOTION_CLASS_MELEE'"]:
            self.setUp();self.lua.execute(setup+';callbacks.Combat(combat(1))')
            self.assertEqual(self.lua.globals().awards,0,setup)
    def test_defending_recon(self):
        self.lua.execute('local c=combat(1);c.attacker,c.defender=c.defender,c.attacker;callbacks.Combat(c)')
        self.assertEqual(self.lua.globals().awards,1)

class HousingTests(unittest.TestCase):
    def test_actual_report_collection_filters_completed_specialty_districts(self):
        if not (ROOT.parent/'Better_Report/RealModifierAnalysis.lua').is_file():
            self.skipTest('Installed Better Report Screen required')
        lua=lua_runtime()
        lua.execute('''
          GlobalParameters={BRS_VERSION_MAJOR=6,BRS_VERSION_MINOR=1}
          ExposedMembers={}; Modding={IsModActive=function() return true end}
          YieldTypes={FOOD=0,PRODUCTION=1,GOLD=2,SCIENCE=3,CULTURE=4,FAITH=5}
          GameInfo=setmetatable({DistrictReplaces={DISTRICT_SEOWON={ReplacesDistrictType='DISTRICT_CAMPUS'}}},
            {__index=function(t,k) local empty=setmetatable({}, {__call=function() return function() end end});rawset(t,k,empty);return empty end})
          Game={GetLocalPlayer=function() return 0 end}
        ''')
        source=(ROOT.parent/'Better_Report/RealModifierAnalysis.lua').read_text(encoding='utf-8-sig')
        # Strip Firaxis' optional type annotations to execute the installed
        # dependency in standard Lua. Nothing is copied into the release.
        source=re.sub(r':\s*(?:table|number|string|boolean|ifunction)\b','',source)
        lua.execute(source)
        lua.execute((ROOT/'UI/Housing.lua').read_text())
        lua.execute('''
          tCities={A={Districts={
            {SubjectType='District',DistrictType='DISTRICT_CAMPUS',isBuilt=true},
            {SubjectType='District',DistrictType='DISTRICT_CAMPUS',isBuilt=false},
            {SubjectType='District',DistrictType='DISTRICT_CITY_CENTER',isBuilt=true}}},
          B={Districts={{SubjectType='District',DistrictType='DISTRICT_SEOWON',isBuilt=true}}}}
          modifier={CollectionType='COLLECTION_PLAYER_DISTRICTS',EffectType='EFFECT_ADJUST_DISTRICT_HOUSING',Arguments={Amount=2},
            SubjectReqSet={TestAny=true,Reqs={{ReqType='REQUIREMENT_DISTRICT_TYPE_MATCHES',Arguments={DistrictType='DISTRICT_CAMPUS'}}}}}
          subjects,subjectType=BuildCollectionOfSubjects(modifier,{SubjectType='Player'},'Player')
          total=YieldTableNew()
          for _,subject in ipairs(subjects) do YieldTableAdd(total,ApplyEffectAndCalculateImpact(modifier,subject,subjectType)) end
        ''')
        self.assertEqual(len(lua.globals().subjects),2)
        self.assertEqual(lua.globals().total.HOUSING,4)
    def test_extension_and_local_player(self):
        lua=lua_runtime()
        lua.execute('''
          function YieldTableNew() return {HOUSING=0} end
          function ApplyEffectAndCalculateImpact() return 'original' end
          function CalculateModifierEffect(kind,object,player) return player end
          ExposedMembers={RMA={}}; Game={GetLocalPlayer=function() return 3 end}
        ''')
        lua.execute((ROOT/'UI/Housing.lua').read_text())
        self.assertEqual(lua.eval("ApplyEffectAndCalculateImpact({EffectType='EFFECT_ADJUST_DISTRICT_HOUSING',Arguments={Amount='2'}},{SubjectType='District'},'District').HOUSING"),2)
        self.assertEqual(lua.eval("ApplyEffectAndCalculateImpact({EffectType='OTHER'},{},'City')"),'original')
        self.assertIsNone(lua.eval("ApplyEffectAndCalculateImpact({EffectType='EFFECT_ADJUST_DISTRICT_HOUSING',Arguments={Amount=2}},{SubjectType='City'},'City')"))
        self.assertEqual(lua.eval("ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_MEDINA_QUARTER',0)"),3)

class RepairUITests(unittest.TestCase):
    def setUp(self):
        self.lua=lua_runtime()
        self.lua.execute('''
          revision=0;panel=0;tabs=0;production=0;resources=0;report=0;selectedID=1;hidden=false;closes=0
          ContextPtr={LookUpControl=function() return {IsHidden=function() return hidden end} end}
          Game={GetLocalPlayer=function() return 0 end}
          city={GetID=function() return 1 end,GetProperty=function() return revision end}
          Players={[0]={GetCities=function() return {Members=function() return ipairs({city}) end} end}}
          UI={GetHeadSelectedCity=function() return {GetID=function() return selectedID end,GetOwner=function() return 0 end} end}
          LuaEvents={RefreshCityPanel=function() panel=panel+1 end,CityPanelTabRefresh=function() tabs=tabs+1 end,
            CQUI_ProductionPanel_CityviewDisable=function() closes=closes+1 end,
            CQUI_ProductionPanel_CityviewEnable=function() production=production+1 end,UE_RefreshTopPanel=function() resources=resources+1 end}
          ExposedMembers={RMA={RefreshBaseData=function() report=report+1 end}}
        ''')
        self.lua.execute((ROOT/'UI/RepairRefresh.lua').read_text())
    def test_refresh_once_after_gameplay_revision(self):
        self.lua.execute('callbacks.GameCoreEventPublishComplete();revision=1;callbacks.GameCoreEventPublishComplete();callbacks.GameCoreEventPublishComplete()')
        for count in ['panel','tabs','production','resources','report']:
            self.assertEqual(self.lua.globals()[count],1,count)
    def test_other_city_does_not_replace_selected_city(self):
        self.lua.execute('selectedID=2;revision=1;callbacks.GameCoreEventPublishComplete()')
        self.assertEqual(self.lua.globals().panel,0)
        self.assertEqual(self.lua.globals().resources,1)
    def test_hidden_production_panel_stays_hidden(self):
        self.lua.execute('hidden=true;revision=1;callbacks.GameCoreEventPublishComplete()')
        self.assertEqual(self.lua.globals().production,0)
        self.assertEqual(self.lua.globals().closes,0)
    def test_reload_refresh_does_not_mutate_gameplay(self):
        self.lua.execute('revision=4;callbacks.LoadGameViewStateDone()')
        self.assertEqual(self.lua.globals().revision,4)
        self.assertEqual(self.lua.globals().production,1)

if __name__=='__main__': unittest.main(verbosity=2)
