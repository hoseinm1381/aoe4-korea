# Korea 0.3.6

The 0.3.5 match screenshots showed pale roofs and high-saturation owner colour on the paving. Nine unique structures now have separate palettes and matte material maps. They use painted wood, iron-grey and charcoal roof tiles, natural stone variation, and different timber and trim finishes. The dynamic owner material uses a neutral colour base and its own red mask. Raised, connected surfaces route to that mask, with base paving excluded.

| Model | Art direction |
| --- | --- |
| Bulguksa Temple | Pine-green bracket bands, weathered red beams, and grey-brown masonry |
| Gate of Reverence | Sungnyemun-inspired cinnabar timber and evergreen trim over charcoal tiles and a darker masonry gate |
| Gyeongbok Palace | Dark blue-black roof tiles, cinnabar and jade framing, and warm gilt accents |
| Hall of Worthies | Chestnut wood, ochre details, and warm slate |
| Hwangnyongsa | Silla-inspired red earth pigments, mineral blue accents, and dark tile. The original wooden structure survives as an archaeological site, so the paint is an interpretation |
| Mountain Fortress | Dark pine and umber gates over varied rubble stone |
| Seon Deok Observatory | Weathered olive-grey masonry, darker timber, and raised owner accents |
| Seowon Academy | Restrained reddish-brown wood, natural plaster and lattice, and a charcoal-brown roof |
| Stone Pagoda | Jeongnimsa-inspired five-tier silhouette with weathered granite and darker ledges. Dynamic raised trim is a game accent |

The Stone Pagoda's visual width and depth increase by 30%. Its tower rises from approximately 7.82 m to 11.26 m by adding height above the plinth. The geometry transform covers construction, damage, ruins, and all finished LODs. The gameplay footprint and stamp placements retain their existing sizes.

The native red mask measures 6.60–9.50% by decoded triangle area across finished LODs. Each asset has a unique albedo, and all nine share the normal, matte, and owner maps. See [native model readback](update_036/landmark-native-readback.json). The Blender review simulates the player tint. A fresh AoE IV match is required to qualify the actual engine colour response.

## Gameplay and card

Both Korean barrage weapons now use a 6-second default native reload, up from 3 seconds. The ability recharge and existing burst duration retain their current values. The normal Keep can issue its barrage after construction without requiring a landmark state. The Palace continues to use its active-state guard during firing, ruin and repair. In the supplied test session the diagnostic log showed one call reaching `barrage.entity_attack` at 508.625 s and a later call at 529.500 s returning before modifiers or the attack command. The source showed the shared landmark-only readiness gate.

The Codex now connects 33 related tier icons per variant with the same vertical segment length convention used in Chagatai. Existing icon positions and requirements were retained. The initial card shows **668–1592**.

## Historical references

- Jeongnimsa's five-story granite pagoda and upward stone eaves. [Korea Heritage Service](https://www.heritage.go.kr/heri/cul/culSelectDetail.do?ccbaCpno=1113400090000&pageNo=1_1_1_1) · [Buyeo County](https://www.buyeo.go.kr/html/tour/info/info_010102.html)
- Painted Korean floral and geometric motifs. [Korea Post](https://koreastamp.epost.go.kr/sp/eg/speg0302.jsp?tbsmh01seqnum=5263&tbsmh15seqnum=4235)
- Timber gate above a stone passage. [Korea Tourism Organization, Sungnyemun](https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=111038)
- Masonry, academy timberwork, and mountain fortification. [UNESCO Bulguksa](https://whc.unesco.org/en/list/736/) · [UNESCO Seowon](https://whc.unesco.org/en/list/1498/) · [UNESCO mountain fortresses](https://whc.unesco.org/en/tentativelists/5488/)
- Ancient Silla observatory and archaeological evidence for the wooden wonder. [Korea Tourism Organization, Cheomseongdae](https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=94442) · [National Research Institute of Cultural Heritage, Hwangnyongsa](https://www.nrich.go.kr/english/page.do?menuIdx=1051)

## Source and verification

The editable paint and shared material maps are under `authoring/art036`. The scripts in `tools/art036` document native UV placement, Pagoda scaling, overlay composition, and readback. The regular `BUILD.cmd` consumes the maintained tables, SCAR, and indexed native assets. The local package is assembled by applying the versioned allowlist to the verified 0.3.5 archive, then validating the typed Garrison recipe and reading the result back. The 0.3.5 package is kept as a verified rollback.

Twenty-one scripted and native-data regressions passed, including an ordinary Keep with no landmark active state. The fresh-match Keep shot, Palace repair lifecycle, player colours, and Codex rendering remain separate in-game checks.

The playable ZIP is 211,636,342 bytes (+7,407,781 from 0.3.5). Its 383,150,131-byte SGA passed CRC and SHA checks on all 10,392 members. The allowlist changed 23 members and added 12 textures. The new native texture streams occupy 7,469,766 archive bytes and 31,457,728 bytes in BC3 with mipmaps (125,829,136 bytes as expanded RGBA8). These are summed asset sizes. [Full package receipt](BUILD_VERIFICATION.json).
