"""Reproduce Korea-only native research tooltips without cooking or packaging.

The additive mod must not register resource_type_info/merc_byz a second time.
Keep stock tooltip templates verbatim and add explicit templates selected only
by Korean paid research abilities. Native tuning continues to own affordability
and charging. Merc_byz/action have no native ability cost modifier; these labels
must exactly match the maintained ability fees, checked before any future build.
"""
import gzip,re,sys
from pathlib import Path
from runtime import ROOT as R,read_json,import_table,rgd,at

def render():
 source=gzip.decompress((R/'docs/update_016_research/official-issuabletooltip.xaml.gz').read_bytes()).decode('utf-8-sig')
 a=source.index('    <Style x:Key="DefaultIssuableTooltipDataTemplate"');b=source.index('\n    <models:DataTemplateSourceSelector',a)
 style=source[a:b];start=style.index('                            <ItemsControl Margin="0,10,0,0"');end=style.index('                            </ItemsControl>',start)+len('                            </ItemsControl>')
 names=re.findall(r'\["ability"\]="[^"]+:([^"\n]+)"',(R/'source/scar/korea/catalog.scar').read_text())
 styles={}
 for name in names:
  doc=rgd.read(import_table(read_json(R/'source/tables/attrib/abilities/korea'/f'{name}.rgd.json')))
  canonical={n.key:n.value for n in at(doc,'default/ability_bag/cost_to_player').value}
  for variant in doc.nodes:
   if not isinstance(variant.value,list):continue
   try:bag=at(variant,'ability_bag')
   except StopIteration:continue
   costs={n.key:n.value for n in at(bag,'cost_to_player').value}
   if costs!=canonical:raise ValueError('Research variant has a different fee: '+name+'/'+variant.key)
   if at(bag,'validate_actions').value is not False:raise ValueError('SCAR research must not validate an empty native action tree: '+name)
   if not costs.get('merc_byz',0):continue
   if set(k for k,v in costs.items() if v)-{'merc_byz','action'}:raise ValueError('Mixed Literature fee needs a reviewed tooltip: '+name)
   if costs.get('action',0) not in (0,1):raise ValueError('Unreviewed foreign allowance cost')
   fee={'literature':costs['merc_byz'],'allowance':costs.get('action',0)}
   key=f'KoreaLiterature{int(fee["literature"])}'+('Foreign' if fee['allowance'] else '')+'DataTemplate'
   if at(bag,'ui_info/tooltip_data_template').value!=key:raise ValueError('Research tooltip and price differ: '+name)
   styles[key]=fee
 append=[]
 for name,fee in sorted(styles.items()):
  extra='\n                                <TextBlock Text="1 foreign research choice" Style="{StaticResource nHUDBaseHeavyTextBlockStyle}" />' if fee['allowance'] else ''
  panel='''                            <StackPanel Margin="0,10,0,0" VerticalAlignment="Top">
                                <StackPanel Orientation="Horizontal">
                                    <Image Width="26" Height="20" Source="/WPFGUI;component/icons/korea/bookicon.png" />
                                    <TextBlock Margin="5,0,0,0" Style="{StaticResource nHUDBaseHeavyTextBlockStyle}" Text="'''+f'{fee["literature"]:g} Literature'+'''" />
                                </StackPanel>'''+extra+'\n                            </StackPanel>'
  clone=style[:start]+panel+style[end:];clone=clone.replace('x:Key="DefaultIssuableTooltipDataTemplate"','x:Key="'+name+'Style"',1)
  append.append(clone+'\n    <DataTemplate x:Key="'+name+'" DataType="{x:Type hudModelTypes:IssuableModel}">\n        <ContentControl Content="{Binding}" Style="{StaticResource '+name+'Style}" />\n    </DataTemplate>\n')
 return source.replace('</ResourceDictionary>','\n    <!-- Korea research templates only; stock templates above are preserved verbatim. -->\n'+''.join(append)+'</ResourceDictionary>')

def verify():
 path=R/'source/resources/ui/hud/controls/issuabletooltip.xaml'
 if path.read_bytes()!=render().encode('utf-8'):raise ValueError('Korean research fee labels need regeneration: python tools/research016_ui.py --write')
 print('RESEARCH_TOOLTIP_SOURCE_VERIFIED',path.stat().st_size,flush=True)

if __name__=='__main__':
 if sys.argv[1:]==['--write']:
  (R/'source/resources/ui/hud/controls/issuabletooltip.xaml').write_bytes(render().encode('utf-8'))
 elif sys.argv[1:]:raise SystemExit('Use --write to update the maintained XAML, or no arguments to verify it')
 verify()
