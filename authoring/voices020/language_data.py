"""Editable Korean age-dialogue authoring, 0.2.0.
Original game sentences: reconstructed/projected diction, not historical quotations.
A1 is an explicitly uncertain retrojection; A2/A3 are editorial reconstructions.
A4 uses Middle Korean lexical/grammatical evidence with modern-TTS approximations.
"""
SOURCES={
 'period_old':'https://www.cambridge.org/core/books/abs/korean/historical-background/D9A158DD0C2CEB58F2CFF2CAC6926FBD',
 'period_middle':'https://www.cambridge.org/core/books/abs/history-of-the-korean-language/early-middle-korean/FF9996225A244622289FABDB3810E592',
 'reconstruction_limits':'https://assets.cambridge.org/97805216/61898/excerpt/9780521661898_excerpt.htm',
 'nora':'https://www.korean.go.kr/nkview/nklife/1995_2/5_12.html',
 'na_history':'https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002398451',
 'nireuda':'https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=261&pageIndex=1&qna_seq=323140',
 'gotida':'https://www.korean.go.kr/common/download.do?c_file_name=36d2c7f7-3b41-4633-8bbe-6d1f4a31e115_0.pdf&file_path=reportData&o_file_name=국어책임관 어떤일을하나_본문.pdf',
 'alphabet':'https://m.hangeul.go.kr/lang/en/html/education/Hangeul.do',
 'lost_z':'https://encykorea.aks.ac.kr/Article/E0021565',
 'tone_limits':'https://waks.aks.ac.kr/rsh/dir/rview.aspx?dataID=AKS-2013-CKD-1240001_DIC%4000003337&rshID=AKS-2013-CKD-1240001',
 'wood_primary':'https://ko.wikisource.org/wiki/페이지:언역_분류두공부시_(009).pdf/13'
}
AGE_NOTES={
 1:{'period':'Silla / Old Korean game-age projection','text_confidence':'low','basis':['period_old','reconstruction_limits','nora','na_history'],'limit':'Middle Korean-informed retrojection, not an attested Silla sentence or recovered Silla recording.'},
 2:{'period':'Goryeo / Early Middle Korean projection','text_confidence':'low-to-moderate','basis':['period_middle','reconstruction_limits','nora'],'limit':'Creative response sentences informed by later grammatical evidence; no exact Goryeo utterance attestation.'},
 3:{'period':'Late Goryeo / early Joseon editorial transition','text_confidence':'moderate for cited lexemes; low for full-sentence dating','basis':['period_middle','nora','nireuda','gotida'],'limit':'Game-age bridge, not a separately established linguistic stage.'},
 4:{'period':'Joseon / Late Middle Korean-inspired game dialogue','text_confidence':'moderate for cited forms; original composed utterances','basis':['alphabet','nora','nireuda','gotida','wood_primary'],'limit':'Full pitch accents, old clusters, precise araea and lost fricatives are not validated by modern Korean TTS.'}
}
# First selection response identifies the unit's actual equipment/work. Other
# alternatives use general acknowledgements in that same original actor voice.
ITEMS={
 'VILLAGER_M':('일할 연장','work tools'),'VILLAGER_F':('일할 연장','work tools'),
 'SCOUT':('길 볼 채비','scouting gear'),'SCOUT_F':('길 볼 채비','scouting gear'),
 'SPEARMAN':('창','spear'),'ARCHER':('활','bow'),'CROSSBOW':('살','crossbow bolts'),
 'GAPSA':('창과 방패','spear and shield'),'TIGER_HUNTER':('사냥살','hunting arrows'),
 'HANDCANNON':('총통','hand cannon'),'HORSEMAN':('고삐','reins'),'LANCER':('긴 창','long lance'),
 'HWARANG_FOOT':('활','bow'),'HWARANG_MOUNTED':('말','horse'),
 'SCHOLAR':('책','book'),'MONK':('경전','Buddhist scripture'),'RIGHTEOUS_MONK':('칼','sword'),
 'MILITIA':('막을 연장','defensive tools'),'TRADER':('팔 것','trade goods'),
 'RAM':('굵은 나모','ram beam'),'TREBUCHET':('큰 돌','large stones'),
 'HWACHA':('화전','fire arrows'),'BOMBARD':('화포','cannon'),'SPRINGALD':('큰 살','large bolts'),
 'NAVAL_FISHING':('그믈','fishing net'),'NAVAL_TRANSPORT':('실을 자리','transport space'),
 'NAVAL_TRADE':('팔 것','trade cargo'),'NAVAL_COMBAT_SHIP':('살과 노','arrows and oars'),
 'NAVAL_WAR_GALLEY':('큰 노','galley oars'),'NAVAL_COMBAT_WARSHIP':('화포','ship cannon'),
 'NAVAL_TURTLE':('귀선','turtle ship'),'NAVAL_FIRESHIP':('불','fire')}
RANGED={'ARCHER','CROSSBOW','TIGER_HUNTER','HANDCANNON','HWACHA','BOMBARD','SPRINGALD','TREBUCHET','NAVAL_COMBAT_SHIP','NAVAL_WAR_GALLEY','NAVAL_COMBAT_WARSHIP','NAVAL_TURTLE'}
# A phonetic respelling is only an approximation, never proof of reconstructed
# pronunciation. These changes deliberately preserve audible older vowel/lexeme
# distinctions where ordinary modern Korean input would silently modernize them.
RESPELL={'ᄒᆞ':'허','ᄅᆞᆯ':'럴','ᄅᆞ':'러','ᄋᆞᆯ':'얼','ᄋᆞ':'어','ᄆᆞ':'머','ᄊᆞᆷ':'썸'}
POOLS={}
# Each row is [meaning, Age I, Age II, Age III, Age IV]. Original composition.
POOLS['select']=[
 ['I am listening.','듣노라.','말ᄊᆞᆷ 듣노라.','말ᄊᆞᆷ 들으리라.','말ᄊᆞᆷ 들으리이다.'],
 ['I await your direction.','내 듣노라.','내 명을 듣노라.','명을 기다리리라.','명을 기다리리이다.'],
 ['I accept the task.','일 맡노라.','내 일 맡노라.','그 일 맡으리라.','그 일을 맡으리이다.'],
 ['I stand ready.','굳게 서노라.','내 굳게 서노라.','굳게 서리라.','굳게 서리이다.'],
 ['I follow your words.','따르노라.','말ᄊᆞᆷ 따르노라.','말ᄊᆞᆷ 따르리라.','말ᄊᆞᆷ 따르리이다.'],
 ['I am ready to work.','일 ᄒᆞ노라.','일할 채비ᄒᆞ노라.','일할 채비ᄒᆞ리라.','이제 일할 채비ᄒᆞ리이다.']]
POOLS['acknowledge']=[
 ['I heed your words.','말ᄊᆞᆷ 듣노라.','내 말ᄊᆞᆷ 듣노라.','그 말ᄊᆞᆷ 들으리라.','그 말ᄊᆞᆷ 들으리이다.'],
 ['I comply.','내 따르노라.','이제 따르노라.','그리 따르리라.','그리 따르리이다.'],
 ['I receive your order.','명 받노라.','내 명을 받노라.','명을 받으리라.','명을 받으리이다.'],
 ['I do it at once.','곧 ᄒᆞ노라.','곧 일 ᄒᆞ노라.','곧 그리 ᄒᆞ리라.','곧 그리 ᄒᆞ리이다.'],
 ['I do as directed.','이리 ᄒᆞ노라.','내 그리 ᄒᆞ노라.','말대로 ᄒᆞ리라.','말대로 ᄒᆞ리이다.'],
 ['I take responsibility.','내 맡노라.','내 그 일 맡노라.','내 맡아 ᄒᆞ리라.','내 맡아 ᄒᆞ리이다.']]
POOLS['move']=[
 ['I go.','가노라.','그리로 가노라.','그리로 가리라.','그리로 가리이다.'],
 ['I follow the road.','길 가노라.','길 따라 가노라.','길 따라 가리라.','길 따라 가리이다.'],
 ['I advance.','나아가노라.','곧 나아가노라.','곧 나아가리라.','곧 나아가리이다.'],
 ['I move as ordered.','내 가노라.','말ᄊᆞᆷ 따라 가노라.','말ᄊᆞᆷ 따라 가리라.','말ᄊᆞᆷ 따라 가리이다.'],
 ['I go ahead.','앞서 가노라.','앞서 길 보노라.','앞서 길 보리라.','앞서 길 보리이다.'],
 ['I set forth.','발 옮기노라.','이제 발 옮기노라.','발 옮겨 가리라.','발 옮겨 가리이다.']]
POOLS['sail']=[
 ['I travel the waterway.','믈길 가노라.','믈길로 가노라.','믈길로 가리라.','믈길로 가리이다.'],
 ['I row onward.','노 젓노라.','앞서 노 젓노라.','앞서 노 저으리라.','앞서 노 저으리이다.'],
 ['I follow the current.','믈 따라 가노라.','흐르는 믈 따라 가노라.','믈 따라 나아가리라.','믈 따라 나아가리이다.'],
 ['I set out on the water.','믈로 나아가노라.','이제 믈로 나아가노라.','곧 믈로 나아가리라.','곧 믈로 나아가리이다.'],
 ['I steer toward that place.','저리 가노라.','저 믈길 따라 가노라.','저 믈길 따라 가리라.','저 믈길 따라 가리이다.'],
 ['I prepare the oars.','노 갖추노라.','노 갖추고 가노라.','노 갖추고 가리라.','노 갖추고 가리이다.']]
POOLS['attack']=[
 ['I strike.','티노라.','적을 티노라.','적을 티리라.','적을 티리이다.'],
 ['I resist the enemy.','막노라.','적을 막노라.','적을 막으리라.','적을 막으리이다.'],
 ['I advance to strike.','나아가 티노라.','앞서 나아가 티노라.','나아가 티리라.','앞서 나아가 티리이다.'],
 ['I gather my strength.','힘 모으노라.','티려 힘 모으노라.','힘 모아 티리라.','힘 모아 티리이다.'],
 ['I defend our side.','우리 지키노라.','우리 편 지키노라.','우리 편 지키리라.','우리 편 지키리이다.'],
 ['I meet the enemy.','적 맞노라.','앞서 적 맞노라.','앞서 적 맞으리라.','앞서 적 맞으리이다.']]
POOLS['shoot']=[
 ['I shoot.','쏘노라.','적을 쏘노라.','적을 쏘리라.','적을 쏘리이다.'],
 ['I aim.','겨누노라.','적을 겨누노라.','적을 겨누리라.','적을 겨누리이다.'],
 ['I prepare ammunition.','쏠 것 갖추노라.','쏠 것 갖추고 겨누노라.','쏠 것 갖추리라.','쏠 것 갖추리이다.'],
 ['I block the enemy.','적 막노라.','쏘아 적 막노라.','쏘아 적 막으리라.','쏘아 적 막으리이다.'],
 ['I find an opening.','틈 보노라.','쏠 틈 보노라.','쏠 틈 보리라.','쏠 틈 보리이다.'],
 ['I fire with our side.','함께 쏘노라.','우리 함께 쏘노라.','우리 함께 쏘리라.','우리 함께 쏘리이다.']]
POOLS['under_attack']=[
 ['I am being struck.','내 맞노라.','내 몸 맞노라.','굳게 버티리라.','굳게 버티리이다.'],
 ['I defend myself.','적 막노라.','힘 다ᄒᆞ여 막노라.','힘 다ᄒᆞ여 막으리라.','힘 다ᄒᆞ여 막으리이다.'],
 ['I lower myself for cover.','몸 낮추노라.','몸 낮추어 버티노라.','몸 낮추어 버티리라.','몸 낮추어 버티리이다.'],
 ['I fall back.','물러서노라.','적 피해 물러서노라.','적 피해 물러서리라.','적 피해 물러서리이다.'],
 ['I seek safety.','살길 찾노라.','내 살길 찾노라.','살길 찾아 버티리라.','살길 찾아 버티리이다.'],
 ['I hold with all my strength.','힘 다ᄒᆞ노라.','내 힘 다ᄒᆞ노라.','힘 다ᄒᆞ여 버티리라.','힘 다ᄒᆞ여 버티리이다.']]
POOLS['build']=[
 ['I build.','짓노라.','내 짓노라.','이제 지으리라.','이제 지으리이다.'],
 ['I prepare the ground.','터 닦노라.','지을 터 닦노라.','터 닦아 지으리라.','터 닦아 지으리이다.'],
 ['I build with our hands.','함께 짓노라.','일손 모아 짓노라.','일손 모아 지으리라.','일손 모아 지으리이다.'],
 ['I build it firmly.','굳게 짓노라.','내 굳게 짓노라.','굳게 지으리라.','굳게 지으리이다.'],
 ['I gather what construction needs.','쓸 것 모으노라.','쓸 것 모아 짓노라.','쓸 것 모아 지으리라.','쓸 것 모아 지으리이다.'],
 ['I take up the building work.','손으로 짓노라.','내 손으로 짓노라.','내 손으로 지으리라.','내 손으로 지으리이다.']]
POOLS['repair']=[
 ['I repair it.','고티노라.','내 고티노라.','다시 고티리라.','다시 고티리이다.'],
 ['I mend the damaged part.','상한 것 고티노라.','상한 데 고티노라.','상한 데 고티리라.','상한 데 고티리이다.'],
 ['I set it right.','바로잡노라.','고티어 바로잡노라.','고티어 바로잡으리라.','고티어 바로잡으리이다.'],
 ['I work on it carefully.','살펴 고티노라.','잘 살펴 고티노라.','잘 살펴 고티리라.','잘 살펴 고티리이다.'],
 ['I make it sound again.','다시 고티노라.','다시 굳게 고티노라.','다시 굳게 고티리라.','다시 굳게 고티리이다.'],
 ['I use my hands to repair.','손으로 고티노라.','내 손으로 고티노라.','내 손으로 고티리라.','내 손으로 고티리이다.']]
POOLS['wood']=[
 ['I cut wood.','나모 버히노라.','쓸 나모 버히노라.','쓸 나모 버히리라.','쓸 나모 버히리이다.'],
 ['I gather wood.','나모 모으노라.','쓸 나모 모으노라.','쓸 나모 모으리라.','쓸 나모 모으리이다.'],
 ['I look for good wood.','나모 찾노라.','좋은 나모 찾노라.','좋은 나모 찾으리라.','좋은 나모 찾으리이다.'],
 ['I cut here.','여기 버히노라.','여기 나모 버히노라.','이 나모 버히리라.','이 나모 버히리이다.'],
 ['I work the timber.','나모 일 ᄒᆞ노라.','나모로 일 ᄒᆞ노라.','나모 일 ᄒᆞ리라.','나모 일 ᄒᆞ리이다.'],
 ['I bring more wood.','나모 더 모으노라.','쓸 나모 더 모으노라.','나모 더 모으리라.','나모 더 모으리이다.']]
POOLS['gold']=[
 ['I mine gold.','금 캐노라.','내 금을 캐노라.','금을 캐리라.','금을 캐리이다.'],
 ['I gather gold.','금 모으노라.','쓸 금 모으노라.','쓸 금 모으리라.','쓸 금 모으리이다.'],
 ['I look for gold.','금 찾노라.','땅에셔 금 찾노라.','금 찾아 캐리라.','금 찾아 캐리이다.'],
 ['I dig gold from the earth.','땅 파노라.','금 있는 땅 파노라.','금 있는 땅 파리라.','금 있는 땅 파리이다.'],
 ['I gather precious metal.','귀한 금 모으노라.','귀한 금을 모으노라.','귀한 금 모으리라.','귀한 금 모으리이다.'],
 ['I collect more gold.','금 더 모으노라.','쓸 금 더 모으노라.','금 더 모으리라.','금 더 모으리이다.']]
POOLS['stone']=[
 ['I quarry stone.','돌 캐노라.','쓸 돌을 캐노라.','쓸 돌 캐리라.','쓸 돌 캐리이다.'],
 ['I break the stone.','돌 깨노라.','굳은 돌 깨노라.','굳은 돌 깨리라.','굳은 돌 깨리이다.'],
 ['I gather stone.','돌 모으노라.','쓸 돌 모으노라.','쓸 돌 모으리라.','쓸 돌 모으리이다.'],
 ['I dig for stone.','땅에셔 돌 캐노라.','땅에셔 쓸 돌 캐노라.','땅 파서 돌 캐리라.','땅 파서 돌 캐리이다.'],
 ['I find strong stone.','굳은 돌 찾노라.','쓸 만한 돌 찾노라.','굳은 돌 찾으리라.','굳은 돌 찾으리이다.'],
 ['I gather more stone.','돌 더 모으노라.','쓸 돌 더 모으노라.','돌 더 모으리라.','돌 더 모으리이다.']]
POOLS['food']=[
 ['I gather food.','먹을 것 모으노라.','내 먹을 것 모으노라.','먹을 것 모으리라.','먹을 것 모으리이다.'],
 ['I find food.','먹을 것 찾노라.','쓸 먹을 것 찾노라.','먹을 것 찾으리라.','먹을 것 찾으리이다.'],
 ['I bring food in.','먹을 것 거두노라.','우리 먹을 것 거두노라.','먹을 것 거두리라.','먹을 것 거두리이다.'],
 ['I work for our provisions.','먹을 일 ᄒᆞ노라.','우리 먹을 일 ᄒᆞ노라.','먹을 일 ᄒᆞ리라.','먹을 일 ᄒᆞ리이다.'],
 ['I gather provisions together.','함께 모으노라.','먹을 것 함께 모으노라.','함께 먹을 것 모으리라.','함께 먹을 것 모으리이다.'],
 ['I gather more food.','먹을 것 더 모으노라.','먹을 것을 더 모으노라.','먹을 것 더 거두리라.','먹을 것 더 거두리이다.']]
POOLS['trade']=[
 ['I receive payment.','값 받노라.','팔고 값 받노라.','팔고 값 받으리라.','팔고 값 받으리이다.'],
 ['I exchange goods.','바꾸노라.','물건 바꾸노라.','물건 바꾸리라.','물건 바꾸리이다.'],
 ['I load trading goods.','팔 것 싣노라.','바꿀 것 싣노라.','바꿀 것 실으리라.','바꿀 것 실으리이다.'],
 ['I travel the trade road.','길로 가노라.','값 찾아 길 가노라.','값 찾아 길 가리라.','값 찾아 길 가리이다.'],
 ['I prepare goods for sale.','팔 것 갖추노라.','팔 것을 갖추노라.','팔 것 갖추리라.','팔 것 갖추리이다.'],
 ['I return from a long journey.','먼 길 가노라.','먼 길 다녀오노라.','먼 길 다녀오리라.','먼 길 다녀오리이다.']]
POOLS['fish']=[
 ['I catch fish.','고기 잡노라.','내 고기 잡노라.','고기 잡으리라.','고기 잡으리이다.'],
 ['I cast the net.','그믈 드리노라.','이 믈에 그믈 드리노라.','그믈 드리리라.','그믈 드리리이다.'],
 ['I pull in the net.','그믈 걷노라.','내 그믈 걷노라.','그믈 거두리라.','그믈 거두리이다.'],
 ['I search the water for fish.','고기 찾노라.','믈속 고기 찾노라.','믈속 고기 찾으리라.','믈속 고기 찾으리이다.'],
 ['I gather fish for food.','고기 모으노라.','먹을 고기 모으노라.','먹을 고기 모으리라.','먹을 고기 모으리이다.'],
 ['I fish in this water.','여기 고기 잡노라.','이 믈에셔 고기 잡노라.','여기 고기 잡으리라.','여기 고기 잡으리이다.']]
