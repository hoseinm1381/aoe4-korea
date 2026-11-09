# Korea 0.3.5

Nine Korean landmark, keep, and wonder models use a shared painted atlas with warmer stone, darker roof tiles, lacquered timber, and dancheong-inspired painted trim. Bulguksa Temple had less than 5% player-colour coverage on the finished mesh in 0.3.4. Its three LODs now measure 10.53–13.01%. The other eight models use the same revised dynamic mask. The two work-camp shelters had blank masks. Their timber now carries player colour and is distinct from the granite and reed thatch. Forty-three ordinary building models reuse eight warmer plaster and stone finishes through their original layered materials.

[Korea Post documents the floral and geometric dancheong bands that inspired the painted trim.](https://koreastamp.epost.go.kr/sp/eg/speg0302.jsp?tbsmh01seqnum=5263&tbsmh15seqnum=4235)

## Coverage and verification

Coverage is the share of decoded triangle area sampled by the red owner mask at or above 128. Finished landmark LODs measure 10.53–19.46%. The camp estimates are 9.87% for the lumber camp and 5.77% for the mining camp. The camp denominator includes all private machinery geometry groups and the finished shelter. It excludes incidental stamp props. The ordinary layered surfaces received albedo changes. Their player-colour coverage was outside this mask measurement.

The archive overlay consists of 54 material members and 14 BC3 textures with complete mip chains. The geometry, UVs, LOD partitions, rig data, stamp bindings, controllers, tuning tables, and voice members match 0.3.4. [Architecture and texture budget receipt](update_035/architecture.json).

The [Blender comparison](update_035/architecture-preview.jpg) uses the decoded healthy geometry. The preview shader approximates the selected player colour using the native red mask. Fresh-match rendering, game-camera readability, and native lifecycle behavior still need a game check.

## Rebuild

The original Blender masters remain in `authoring/art013`. The painted RGBA atlases and owner masks are in `authoring/art035`. `tools/art035/architecture.py` stages native RRTex streams and material-only bindings. Its source is the extracted 0.3.4 SGA, along with Garrison `convert decode-static` readbacks for the nine landmark, keep, and wonder models, the two private shelters, and the two ordinary camp machinery models. Use the stock asset index for the ordinary plaster and stone source textures. `tools/art035/preview_blender.py` renders the comparisons in a background Blender process.

The ordinary `BUILD.cmd` route assembles the indexed native inputs into the playable package. The final allowlist and hashes are based on the exact 0.3.4 player SGA. The 0.3.4 ZIP remains available as a local rollback. The fresh release uses the same Garrison 0.1.16 minimum.

## Final package

The playable ZIP is 204,228,561 bytes, +2,613,498 bytes compared with 0.3.4. Its SGA is 375,679,248 bytes. All 10,380 archive members passed readback and 10,312 match 0.3.4 byte for byte. The added streams total 2,647,571 on-disk bytes and 15,379,488 bytes in BC3 with mipmaps. Expanded RGBA8 would use 61,516,440 bytes across the added textures. These are summed asset sizes rather than measured runtime residency.

Thirteen existing starting-state, player-schema, and Literature regressions passed. [Build and ZIP receipt](BUILD_VERIFICATION.json) · [Decoded player-mask results](update_035/final-readback.json).
