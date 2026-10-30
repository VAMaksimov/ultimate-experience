"""Build only our manifest and provenance inventory; never edit upstream mods."""
from pathlib import Path
import hashlib, json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT.parent

def build():
    records = []
    for folder in sorted(MODS.iterdir()):
        if not folder.is_dir() or folder == ROOT:
            continue
        for file in folder.glob('*.modinfo'):
            tree = ET.parse(file).getroot()
            properties = tree.find('Properties')
            workshop = properties.findtext('SubscriptionID') or (re.match(r'^(\d+) ', folder.name).group(1) if re.match(r'^(\d+) ', folder.name) else None)
            links = {'BBG':'https://github.com/CivilizationVIBetterBalancedGame',
                     'CQUI_Community-Edition-main':'https://github.com/Civitas-Collective/CQUI_Community-Edition',
                     'Policy_Cards':'https://steamcommunity.com/sharedfiles/filedetails/?id=2266952591',
                     'Detailed_Map_Tacks':'https://steamcommunity.com/sharedfiles/filedetails/?id=2428969051',
                     'Quick_Deals':'https://steamcommunity.com/sharedfiles/filedetails/?id=2460661464'}
            digest = hashlib.sha256()
            for source in sorted(folder.rglob('*')):
                if source.is_file() and source.suffix.lower() in {'.sql','.xml','.lua','.modinfo'}:
                    digest.update(str(source.relative_to(folder)).encode()); digest.update(source.read_bytes())
            records.append(dict(folder=folder.name, name=properties.findtext('Name'), author=properties.findtext('Authors') or ('CQUI community / Civitas' if folder.name=='CQUI_Community-Edition-main' else 'Not declared in manifest'),
                                mod_id=tree.get('id'), version=tree.get('version') or properties.findtext('Version') or 'Not declared',
                                source=f'https://steamcommunity.com/sharedfiles/filedetails/?id={workshop}' if workshop else links.get(folder.name),
                                licenses=[p.name for p in folder.glob('*LICENSE*')],
                                license_status='See upstream license; dependency only' if list(folder.glob('*LICENSE*')) else 'No root license found; dependency only, no redistribution',
                                source_sha256=digest.hexdigest(), runtime_tested=False,
                                role='excluded' if folder.name.startswith(('2465378070','3468617387')) else 'required' if folder.name in ['BBG','Better_Report','Policy_Cards','CQUI_Community-Edition-main',"2542898147 Sukritact's Oceans"] else 'optional'))
    (ROOT/'installed-mods.json').write_text(json.dumps(records, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    lines=['# Ultimate Experience — Workshop collection','',
           'A BBG-based solo pack with ocean content, policy housing estimates, reconstruction and Survey XP fixes. Subscribe to the original mods and the Ultimate Experience patch. Start a new Gathering Storm game and enable the Oceans game mode.','',
           'Release status: candidate; automated checks pass, full campaign and rendered UI acceptance remain pending.','']
    names={'LOC_BBM_TITLE':'Better Balanced Maps 1.37','LOC_CUSTOM_ERA_MULTIPLIER_NAME':'Custom Era Prolongation','LOC_RUIVO_FIX_ALL':'Repair All Districts and Buildings','LOC_HARMONY_IN_DIVERSITY_NAME':'Harmony in Diversity'}
    for role,title in [('required','Required original mods'),('optional','Optional installed mods — campaign certification pending'),('excluded','Disable these conflicting mods')]:
        lines += ['## '+title,'','| Mod | Author | Installed version |','| --- | --- | --- |']
        for rec in records:
            if rec['role']==role:
                label=names.get(rec['name'],rec['name'])
                label=f"[{label}]({rec['source']})" if rec['source'] else label
                author=rec['author'] if not rec['author'].startswith('LOC_') else 'See linked original project'
                lines.append(f"| {label} | {author} | {rec['version']} |")
        lines.append('')
    lines += ['## Credits and redistribution','',
              'All original mods remain their authors’ work and are installed separately. RUIVO’s reconstruction project inspired the repair feature; this pack implements its own gameplay and interface code. This release includes no third-party Lua, SQL, artwork or compiled assets. Exact source fingerprints and license findings are recorded in installed-mods.json.','',
              'The collection has not yet been published to Steam Workshop. The installed versions, not arbitrary future updates, are the initial compatibility reference.']
    (ROOT/'COLLECTION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    mod = ET.Element('Mod', id='5184c35b-e181-4bf9-8f7a-fdba61ae38a2', version='2')
    props = ET.SubElement(mod,'Properties')
    for name,value in {'Name':'Ultimate Experience','Description':'BBG compatibility, ocean content, policy housing, reconstruction and Survey XP. Requires a new Gathering Storm game. Disable Harmony in Diversity and the original Repair All mod.','Authors':'Ultimate Experience contributors','AffectsSavedGames':'1','CompatibleVersions':'2.0'}.items():
        ET.SubElement(props,name).text=value
    deps = ET.SubElement(mod,'Dependencies')
    for rec in records:
        if rec['role']=='required': ET.SubElement(deps,'Mod',id=rec['mod_id'],title=rec['name'])
    ET.SubElement(deps,'Mod',id='4873eb62-8ccc-4574-b784-dda455e74e68',title='Gathering Storm')
    ET.SubElement(deps,'Mod',id='1B28771A-C749-434B-9053-D1380C553DE9',title='Rise and Fall')
    blocks=ET.SubElement(mod,'Blocks')
    for rec in records:
        if rec['role']=='excluded': ET.SubElement(blocks,'Mod',id=rec['mod_id'],title=rec['name'])
    criteria = ET.SubElement(ET.SubElement(mod,'ActionCriteria'),'Criteria',id='UE_Oceans')
    match = ET.SubElement(criteria,'ConfigurationValueMatches')
    for k,v in {'Group':'Game','ConfigurationId':'GAMEMODE_SUK_OCEANS','Value':'1'}.items(): ET.SubElement(match,k).text=v
    actions=ET.SubElement(mod,'InGameActions')
    def action(kind, name, files=(), order=None, criterion=None, **properties):
        node=ET.SubElement(actions,kind,id=name)
        if order is not None: properties['LoadOrder']=str(order)
        if properties:
            p=ET.SubElement(node,'Properties')
            for k,v in properties.items(): ET.SubElement(p,k).text=v
        if criterion: ET.SubElement(node,'Criteria').text=criterion
        for file in files: ET.SubElement(node,'File').text=file
    action('UpdateDatabase','UE_Capture', ['Data/OceansCapture.sql'],4,'UE_Oceans')
    action('UpdateDatabase','UE_Restore', ['Data/OceansRestore.sql'],8,'UE_Oceans')
    action('UpdateText','UE_TextCapture', ['Text/OceansCapture.sql'],4,'UE_Oceans')
    action('UpdateText','UE_TextRestore', ['Text/OceansRestore.sql'],8,'UE_Oceans')
    action('UpdateDatabase','UE_Reconstruction',['Data/Reconstruction.sql'],200000000)
    action('UpdateText','UE_Text',['Text/English.xml'],20000)
    action('UpdateIcons','UE_Icons',['UI/Icons.sql'],20000)
    action('AddGameplayScripts','UE_Gameplay',['Gameplay/Reconstruction.lua','Gameplay/ReconXP.lua'],20000)
    action('AddUserInterfaces','UE_Refresh',['UI/RepairRefresh.xml'],20000,Context='InGame')
    for context,script in [('RealModifierAnalysis','Housing'),('GovernmentScreen','Government'),('ProductionPanel','Production'),('TopPanel','TopPanel')]:
        action('ReplaceUIScript','UE_'+context,order=20000,LuaContext=context,LuaReplace='UI/'+script+'.lua')
    action('ImportFiles','UE_Imports',[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted((ROOT/'UI').glob('*.lua'))],20000)
    files=ET.SubElement(mod,'Files')
    for sub in ['Data','Gameplay','Text','UI']:
        for p in sorted((ROOT/sub).iterdir()):
            if p.is_file(): ET.SubElement(files,'File').text=p.relative_to(ROOT).as_posix()
    ET.indent(mod)
    ET.ElementTree(mod).write(ROOT/'UltimateExperience.modinfo',encoding='utf-8',xml_declaration=True)
    print('Manifest and dependency inventory built.')

if __name__=='__main__': build()
