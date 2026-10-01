#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bulk generator for 50+ setups/workflows/cases - RU/EN bilingual, clustered, cross-linked."""
import os
from pathlib import Path
WIKI = Path(r"C:\BLENDER ai\WIKI")

SETUPS = [
(15,"comfyui_sdxl","BLENDER + COMFYUI SDXL","AI Texturing","⭐⭐","25-40 min",
 ["ComfyUI локально","SDXL base+refiner","ControlNet depth/canny","Blender texture nodes"],
 "RU: ComfyUI как бэкенд генерации PBR. EN: ComfyUI as PBR backend.",
 "RU: \"Сгенерируй через ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth из viewport\" / EN: \"Generate via ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth from viewport\""),
(16,"automatic1111_api","BLENDER + AUTOMATIC1111 API","AI Texturing","⭐⭐","20 min",
 ["A1111 --api","img2img/inpaint","Blender image editor bridge","Batch queue"],
 "RU: A1111 API как дешевый SD-бэкенд. EN: A1111 API as cheap SD backend.",
 "RU: \"Через A1111 API: img2img strength 0.5, 30 steps, seamless tile\" / EN: \"Via A1111 API: img2img strength 0.5, 30 steps, seamless tiling\""),
(17,"krita_ai_diffusion","BLENDER + KRITA AI DIFFUSION","2D/3D Paint","⭐","15 min",
 ["Krita AI Diffusion plugin","Inpaint/outpaint","Live paint to Blender texture","Layer sync"],
 "RU: Рисуешь в Krita — обновляется в Blender. EN: Paint in Krita — updates in Blender.",
 "RU: \"Настрой Krita AI Diffusion live-sync с Blender текстурой 2k\" / EN: \"Setup Krita AI Diffusion live-sync with Blender 2k texture\""),
(18,"substance_painter_live","SUBSTANCE PAINTER LIVE-LINK","Texturing Pro","⭐⭐","25 min",
 ["FBX/GLTF roundtrip","UDIM workflow","Smart materials","Live link plugin"],
 "RU: Substance → Blender живой линк. EN: Substance → Blender live link.",
 "RU: \"Экспорт FBX с UDIM в Substance, запеки ID/curvature/AO, верни PBR 4k в Blender\" / EN: \"Export FBX with UDIM to Substance, bake ID/curvature/AO, return 4k PBR to Blender\""),
(19,"substance_designer_sbsar","SUBSTANCE DESIGNER SBSAR","Procedural","⭐⭐","20 min",
 ["SBSAR import","Exposed params","Tiling control","Blender shader graph"],
 "RU: Параметрические .sbsar в Blender. EN: Parametric .sbsar in Blender.",
 "RU: \"Импортируй .sbsar кирпич, exposed: mortar width, color variation, roughness\" / EN: \"Import .sbsar brick, exposed: mortar width, color variation, roughness\""),
(20,"zbrush_goz","ZBRUSH GOZ BRIDGE","Sculpt","⭐⭐","15 min",
 ["GoZ button","Polypaint → vertex color","Displacement export","Retopo flow"],
 "RU: Мост ZBrush ↔ Blender через GoZ. EN: ZBrush ↔ Blender via GoZ.",
 "RU: \"GoZ экспорт high-poly, полипейнт в vertex color, displacement 32-bit EXR\" / EN: \"GoZ export high-poly, polypaint to vertex color, 32-bit EXR displacement\""),
(21,"marvelous_clo3d","MARVELOUS / CLO3D CLOTH","Cloth","⭐⭐⭐","30-45 min",
 ["Alembic cache","Garment import","Thickness/solidify","Collision setup"],
 "RU: Одежда из Marvelous в Blender. EN: Garments from Marvelous to Blender.",
 "RU: \"Импорт Alembic одежды, solidify 0.002м, collision с телом, запеки normal\" / EN: \"Import Alembic garment, solidify 0.002m, body collision, bake normal\""),
(22,"rizomuv_bridge","RIZOMUV BRIDGE","UV Pro","⭐⭐","15 min",
 ["FBX roundtrip","Auto seams","Pack islands","UDIM tiles"],
 "RU: Идеальная развертка через RizomUV. EN: Perfect unwrap via RizomUV.",
 "RU: \"Экспорт в RizomUV, auto seams by angle 70°, pack margin 4px, верни UV\" / EN: \"Export to RizomUV, auto seams 70°, pack 4px, return UVs\""),
(23,"realitycapture_scan","REALITYCAPTURE SCAN TO BLENDER","Photogrammetry","⭐⭐⭐","40-60 min",
 ["RC CLI","Laser+photo align","Decimate/retopo","PBR bake 8k"],
 "RU: Фотограмметрия → game-ready. EN: Photogrammetry → game-ready.",
 "RU: \"Импорт RC mesh 5M tris → Quad Remesher 20k → Smart UV → bake 8k→2k\" / EN: \"Import RC 5M mesh → Quad Remesher 20k → Smart UV → bake 8k→2k\""),
(24,"metashape_scan","AGISOFT METASHAPE","Photogrammetry","⭐⭐⭐","40 min",
 ["Align photos","Dense cloud","Mesh+texture","Scale bars"],
 "RU: Metashape → Blender пайплайн. EN: Metashape → Blender pipeline.",
 "RU: \"Импорт Metashape OBJ 8k текстурой, ретопо, UDIM, запеки AO/curvature\" / EN: \"Import Metashape OBJ 8k texture, retopo, UDIM, bake AO/curvature\""),
(25,"polycam_luma","POLYCAM / LUMA / KIRI SCAN","Mobile Scan","⭐","15 min",
 ["NeRF/Gaussian splat","GLB export","Cleanup","Scale fix"],
 "RU: Мобильные сканы → Blender. EN: Mobile scans → Blender.",
 "RU: \"Импорт Polycam GLB, почини масштаб x0.01, удали мусор, ретопо\" / EN: \"Import Polycam GLB, fix scale x0.01, cleanup, retopo\""),
(26,"topogun_quad","TOPOGUN / QUAD DRAW RETOPO","Retopo","⭐⭐","25 min",
 ["Manual retopo","Edge flow","Shrinkwrap","Bake maps"],
 "RU: Ручная ретопология для анимации. EN: Manual retopo for animation.",
 "RU: \"Ретопо лица: loops вокруг глаз/рта, полюса 3/5, shrinkwrap 0.001\" / EN: \"Retopo face: loops around eyes/mouth, 3/5 poles, shrinkwrap 0.001\""),
(27,"mixamo_autorig","MIXAMO AUTO-RIG","Auto Rig","⭐","10 min",
 ["T-pose import","Auto-rig","Skin + fix","MCP batch"],
 "RU: Mixamo риг за 10 минут. EN: Mixamo rig in 10 minutes.",
 "RU: \"Загрузи T-pose FBX, Mixamo auto-rig, скачай 5 анимаций, ретаргет в Blender\" / EN: \"Upload T-pose FBX, Mixamo auto-rig, download 5 anims, retarget in Blender\""),
(28,"accurig_cc","ACCURIG / ACTORCORE RIG","Auto Rig","⭐⭐","20 min",
 ["AccuRig skeleton","ActorCore motions","Blender retarget","Face+body"],
 "RU: Reallusion риггинг. EN: Reallusion rigging.",
 "RU: \"AccuRig скелет, 3 ActorCore анимации, ретаргет на Rigify\" / EN: \"AccuRig skeleton, 3 ActorCore anims, retarget to Rigify\""),
(29,"autorignpro","AUTO-RIG PRO","Rig Pro","⭐⭐⭐","40 min",
 ["Smart rig","Limb alignment","Twist/roll","Game export"],
 "RU: Профессиональный риг ARP. EN: Professional ARP rig.",
 "RU: \"Auto-Rig Pro Smart: spine 5, fingers full, twist, export Unity Humanoid\" / EN: \"Auto-Rig Pro Smart: spine 5, full fingers, twist, export Unity Humanoid\""),
(30,"rigify_advanced","RIGIFY ADVANCED + FACE","Rig","⭐⭐⭐","45 min",
 ["Meta-rig samples","Face rig","Rigify-to-Unity","Correctives"],
 "RU: Rigify + лицо + corrective. EN: Rigify + face + correctives.",
 "RU: \"Rigify human + face rig 52 кости, corrective shapes колени/локти, game export\" / EN: \"Rigify human + 52-bone face, knee/elbow correctives, game export\""),
(31,"makehuman_mpfb","MAKEHUMAN / MPFB","Base Human","⭐","15 min",
 ["MPFB 2.0","Targets/morphs","Clothes proxy","Game base"],
 "RU: Базовые люди MPFB. EN: Base humans MPFB.",
 "RU: \"MPFB: female 1.7м, muscular 0.3, age 25, топология game 12k\" / EN: \"MPFB: female 1.7m, muscular 0.3, age 25, game topo 12k\""),
(32,"daz_diffeomorphic","DAZ → BLENDER (DIFFEOMORPHIC)","Daz Bridge","⭐⭐","30 min",
 ["Diffeomorphic addon","G8/G9 import","Morphs/JCM","Hair/cloth convert"],
 "RU: Daz персонажи в Blender. EN: Daz characters to Blender.",
 "RU: \"Diffeomorphic G8: morphs face/body, JCM on, hair to particle/curves\" / EN: \"Diffeomorphic G8: face/body morphs, JCM on, hair to particles/curves\""),
(33,"cc4_blender","CHARACTER CREATOR 4 → BLENDER","CC Pipeline","⭐⭐","30 min",
 ["CC4 pipeline addon","RL Head/body","Cloth/hair","LOD export"],
 "RU: CC4 → Blender. EN: CC4 → Blender.",
 "RU: \"CC4 export FBX+textures, Blender pipeline addon, LOD + facial profile\" / EN: \"CC4 FBX+textures export, Blender pipeline addon, LOD + facial\""),
(34,"metahuman_blender","METAHUMAN → BLENDER","MetaHuman","⭐⭐⭐","40 min",
 ["Quixel Bridge","DNA/livelink","Groom convert","LOD/render"],
 "RU: MetaHuman для Blender рендера. EN: MetaHuman for Blender render.",
 "RU: \"Quixel Bridge MetaHuman LOD0, groom→curves, materials to Principled\" / EN: \"Quixel Bridge MetaHuman LOD0, groom→curves, to Principled\""),
(35,"readyplayerme","READY PLAYER ME AVATARS","Avatar","⭐","10 min",
 ["GLB API","Mixamo rig","Face photo","Web3/VR"],
 "RU: RPM аватары пачкой. EN: RPM avatars in batch.",
 "RU: \"RPM API: 10 аватаров GLB full-body, Mixamo rig, импорт в Blender коллекцию\" / EN: \"RPM API: 10 GLB full-body avatars, Mixamo rig, import to Blender collection\""),
(36,"vroid_studio","VROID STUDIO → BLENDER","Anime","⭐⭐","20 min",
 ["VRM import","MToon→Principled","Hair bones","Spring/VRM"],
 "RU: Vroid аниме в Blender. EN: Vroid anime to Blender.",
 "RU: \"VRM импорт через VRM addon, MToon→Principled, hair spring bones\" / EN: \"VRM import via VRM addon, MToon→Principled, hair springs\""),
(37,"blenderkit_assets","BLENDERKIT ASSETS","Asset Lib","⭐","10 min",
 ["BlenderKit addon","Drag&drop","Private upload","Royalty-free"],
 "RU: Библиотека BlenderKit. EN: BlenderKit library.",
 "RU: \"BlenderKit: 5 материалов + 3 модели + 1 HDRI, private upload своего ассета\" / EN: \"BlenderKit: 5 materials + 3 models + 1 HDRI, private upload own asset\""),
(38,"fab_epic","FAB.COM (EPIC) PIPELINE","Marketplace","⭐⭐","20 min",
 ["Fab library","Quixel Megascans","Sketchfab migrate","Unreal+Blender"],
 "RU: Fab/Quixel в Blender. EN: Fab/Quixel to Blender.",
 "RU: \"Fab: 3 Megascans surfaces 8k + 2 3D plants, bridge to Blender, UDIM\" / EN: \"Fab: 3 Megascans 8k surfaces + 2 plants, bridge to Blender, UDIM\""),
(39,"quixel_bridge","QUIXEL BRIDGE STANDALONE","Megascans","⭐⭐","20 min",
 ["Bridge export","LOD + maps","Calibrated PBR","Blender plugin"],
 "RU: Quixel Bridge экспорт. EN: Quixel Bridge export.",
 "RU: \"Bridge export: love2d, 4k, LOD0-2, metallic/roughness/normal/AO/displacement\" / EN: \"Bridge export: 4k, LOD0-2, metal/rough/normal/AO/displace\""),
(40,"ambientcg_polyhaven","AMBIENTCG + POLYHAVEN BATCH","Free PBR","⭐","15 min",
 ["Batch download","PBR sets","HDRI batch","MCP search"],
 "RU: Пачка бесплатных PBR. EN: Batch free PBR.",
 "RU: \"Скачай 10 PBR 2k ambientCG+PolyHaven: concrete/wood/metal/fabric + 3 HDRI studio\" / EN: \"Download 10 free 2k PBR ambientCG+PolyHaven + 3 studio HDRIs\""),
(41,"hdri_lighting_lab","HDRI LIGHTING LAB","Lighting","⭐⭐","20 min",
 ["HDRI rotation","Exposure ladder","Light portals","Volumetric"],
 "RU: Лаборатория HDRI света. EN: HDRI lighting lab.",
 "RU: \"HDRI ladder: rotation 0/90/180/270, strength 0.5/1/2, portals on, рендер-превью\" / EN: \"HDRI ladder: rot 0/90/180/270, strength 0.5/1/2, portals, preview renders\""),
(42,"tripo_ai_api","TRIPO AI API","Text/Image-to-3D","⭐⭐","20 min",
 ["Tripo 2.5","Image+text prompt","PBR+rig","GLB/USDZ"],
 "RU: Tripo генерация. EN: Tripo generation.",
 "RU: \"Tripo API: image-to-3D + text refine 'worn leather', PBR, auto-rig quad\" / EN: \"Tripo API: image-to-3D + 'worn leather' refine, PBR, auto-rig\""),
(43,"meshy_api_v4","MESHY API V4","Text-to-3D/Texture","⭐⭐","20 min",
 ["Text-to-3D","Text-to-texture","Remesh/retopo","Animate/rig"],
 "RU: Meshy полный цикл. EN: Meshy full cycle.",
 "RU: \"Meshy: text-to-3D 'stylized orc axe', text-to-texture, auto-UV, rig\" / EN: \"Meshy: text-to-3D 'stylized orc axe', text-to-texture, auto-UV, rig\""),
(44,"rodin_hyper3d","RODIN / HYPER3D GEN","Image-to-3D","⭐⭐","20 min",
 ["Rodin Gen-1","Multi-view","PBR bake","Blender cleanup"],
 "RU: Rodin генерация. EN: Rodin generation.",
 "RU: \"Rodin: front+side фото → 3D, decimate 15k, Smart UV, bake normal\" / EN: \"Rodin: front+side photos → 3D, decimate 15k, Smart UV, bake normal\""),
(45,"hunyuan3d_21","HUNYUAN3D 2.1 LOCAL","Local 3D Gen","⭐⭐⭐","40 min",
 ["Hunyuan Docker","SD+3D pipeline","PBR export","VRAM 12GB+"],
 "RU: Локальный Hunyuan3D. EN: Local Hunyuan3D.",
 "RU: \"Hunyuan3D Docker: text 'cozy cabin' → mesh + PBR 2k, импорт GLB\" / EN: \"Hunyuan3D Docker: 'cozy cabin' → mesh + 2k PBR, import GLB\""),
(46,"shap_e_local","SHAP-E / POINT-E LOCAL","Research Gen","⭐⭐","25 min",
 ["OpenAI Shap-E","Text-to-3D latent","Marching cubes","Cleanup"],
 "RU: Исследовательская генерация. EN: Research generation.",
 "RU: \"Shap-E: 'red chair' → latent → mesh, remesh, scale 1м\" / EN: \"Shap-E: 'red chair' → latent → mesh, remesh, scale 1m\""),
(47,"zero123_instantmesh","ZERO123 / INSTANTMESH","Multi-view 3D","⭐⭐⭐","30 min",
 ["Zero123++ views","InstantMesh LRM","NeRF→mesh","Texture refine"],
 "RU: Мультивью реконструкция. EN: Multi-view reconstruction.",
 "RU: \"Zero123++: 6 views из 1 фото → InstantMesh → textured mesh\" / EN: \"Zero123++: 6 views from 1 photo → InstantMesh → textured mesh\""),
(48,"gaussian_splatting","GAUSSIAN SPLATTING → BLENDER","3DGS","⭐⭐⭐","30 min",
 ["3DGS ply","Splat→mesh","Postshot/Luma","Blender import"],
 "RU: Гауссианы в Blender. EN: Gaussians to Blender.",
 "RU: \"Импорт .ply splat, конверт в mesh (SuGaR), запеки текстуру\" / EN: \"Import .ply splats, convert to mesh (SuGaR), bake texture\""),
(49,"ffmpeg_vse_pipeline","FFMPEG + VSE PIPELINE","Video","⭐⭐","20 min",
 ["VSE strips","Proxy 25%","FFmpeg encode","HDR metadata"],
 "RU: Монтаж+кодирование. EN: Edit+encode.",
 "RU: \"VSE: 3 strips + crossfade + text, proxy 25%, FFmpeg H264 CRF18 + ProRes master\" / EN: \"VSE: 3 strips + cross + text, 25% proxy, FFmpeg H264 CRF18 + ProRes\""),
(50,"davinci_roundtrip","DAVINCI RESOLVE ROUNDTRIP","Color/Edit","⭐⭐","25 min",
 ["EDL/XML","ACES pipeline","CDL/LUT","Back to Blender"],
 "RU: Монтаж/грейдинг туда-обратно. EN: Edit/grade roundtrip.",
 "RU: \"Экспорт EDL+EXR в Resolve, грейд ACES, верни LUT .cube в Blender\" / EN: \"Export EDL+EXR to Resolve, ACES grade, return .cube LUT to Blender\""),
(51,"notion_obsidian_docs","NOTION/OBSIDIAN DOCS SYNC","Docs","⭐","10 min",
 ["Markdown export","Asset registry","Changelog","Search index"],
 "RU: Документация из вики. EN: Docs from wiki.",
 "RU: \"Экспорт WIKI db/*.json → Notion/Obsidian, теги, обратные ссылки\" / EN: \"Export WIKI db JSON → Notion/Obsidian with tags/backlinks\""),
(52,"git_lfs_blend","GIT LFS + BLEND VERSIONING","Versioning","⭐⭐","15 min",
 ["LFS track","Lock files","Blend diff","CI validate"],
 "RU: Версионирование .blend. EN: .blend versioning.",
 "RU: \"Git LFS track *.blend/*.exr/*.fbx, lock мейн-сцены, CI рендер-превью\" / EN: \"Git LFS track blend/exr/fbx, lock mains, CI preview render\""),
(53,"flamenco_farm","FLAMENCO FARM CLUSTER","Render Farm","⭐⭐⭐","40 min",
 ["Manager+workers","Shared storage","Job split","Monitor"],
 "RU: Ферма Flamenco. EN: Flamenco farm.",
 "RU: \"Manager+3 workers, NFS storage, split 1-250 по 25 кадров, мониторинг\" / EN: \"Manager+3 workers, NFS, split 1-250 by 25, monitor\""),
(54,"cloud_render_aws","CLOUD RENDER AWS/GCP","Cloud","⭐⭐⭐","40 min",
 ["Spot instances","Docker Blender","S3 sync","Cost cap"],
 "RU: Облачный рендер. EN: Cloud render.",
 "RU: \"AWS Spot g5.xlarge Docker Blender, S3 sync, budget cap $20\" / EN: \"AWS Spot g5 Docker Blender, S3 sync, $20 cap\""),
(55,"ai_upscale_pipeline","AI UPSCALE PIPELINE","Upscale","⭐","15 min",
 ["ESRGAN/Topaz","Sequence upscale","Denoise+sharpen","EXR safe"],
 "RU: Апскейл рендеров. EN: Upscale renders.",
 "RU: \"Topaz/ESRGAN 2x PNG sequence → denoise → sharpen 0.2, EXR untouched\" / EN: \"Topaz/ESRGAN 2x PNG seq → denoise → sharpen 0.2, keep EXR\""),
(56,"mocap_rokoko","MOCAP ROKOKO / MOVE AI","Mocap","⭐⭐","25 min",
 ["Rokoko Studio","Move.ai video","FBX retarget","Clean curves"],
 "RU: Мокап в Blender. EN: Mocap to Blender.",
 "RU: \"Rokoko FBX → Rigify retarget, foot lock, clean spikes, loop\" / EN: \"Rokoko FBX → Rigify retarget, foot lock, despike, loop\""),
(57,"face_mocap_arkit","FACE MOCAP ARKIT","Face Cap","⭐⭐","20 min",
 ["iPhone LiveLink","52 blendshapes","Shape key map","Audio sync"],
 "RU: Лицевой мокап. EN: Face mocap.",
 "RU: \"ARKit 52 blendshapes → shape keys, smoothing 5, audio lip-sync rough\" / EN: \"ARKit 52 → shape keys, smooth 5, rough lip-sync\""),
(58,"vr_scene_inspection","VR SCENE INSPECTION","VR/XR","⭐⭐","20 min",
 ["Blender XR","Quest Link","Scale check","Annotate"],
 "RU: Проверка сцены в VR. EN: VR scene check.",
 "RU: \"Blender XR session, Quest Link, scale 1:1, аннотации маркерами\" / EN: \"Blender XR, Quest Link, 1:1 scale, marker annotations\""),
(59,"web_viewer_export","WEB VIEWER EXPORT","Web 3D","⭐⭐","20 min",
 ["GLB+Draco","Three.js viewer","KTX2 Basis","GitHub Pages"],
 "RU: Вьювер для сайта. EN: Web viewer.",
 "RU: \"GLB Draco + KTX2, three.js viewer template, deploy GitHub Pages\" / EN: \"Draco GLB + KTX2, three.js template, deploy Pages\""),
(60,"shotgrid_ftrack_sync","SHOTGRID / FTRACK SYNC","Production","⭐⭐⭐","35 min",
 ["Shot entities","Version publish","Review notes","Status sync"],
 "RU: Продакшн-трекинг. EN: Production tracking.",
 "RU: \"ShotGrid: shot/tasks/versions, publish EXR+MP4, review notes → Blender markers\" / EN: \"ShotGrid: shots/tasks/versions, publish EXR+MP4, notes → Blender markers\""),
]

WF = [
(9,"realtime_vj_loop","REALTIME VJ LOOP","Realtime","⭐⭐","Procedural loop 8s, audio-reactive, TouchDesigner bridge"),
(10,"product_turntable","PRODUCT TURNTABLE","Product","⭐","360° turntable 120f, studio HDRI, DOF"),
(11,"archviz_day_night","ARCHVIZ DAY→NIGHT","ArchViz","⭐⭐","Sun+HDRI morph, lightmix, 2 renders blend"),
(12,"crowd_sim_gn","CROWD SIM GN","Simulation","⭐⭐⭐","GN points+instances, avoidance, LOD"),
(13,"destruction_rbd","DESTRUCTION RBD","FX","⭐⭐⭐","Cell fracture + RBD + dust, cache Alembic"),
(14,"cloth_fashion_show","CLOTH FASHION SHOW","Cloth","⭐⭐","Marvelous import + wind + runway loop"),
(15,"fluid_product_splash","FLUID PRODUCT SPLASH","Fluid","⭐⭐⭐","FLIP splash around product, meshing, whitewater"),
(16,"npr_anime_render","NPR ANIME RENDER","Stylized","⭐⭐","Lineart+toon shader, paint texture, grease pencil FX"),
(17,"stop_motion_felt","STOP-MOTION FELT LOOK","Stylized","⭐⭐","Stepped interpolation, fuzz shader, fingerprint normal"),
(18,"isometric_game_art","ISOMETRIC GAME ART","Game","⭐⭐","Ortho 54.7°, tileable, atlas, Godot export"),
(19,"voxel_art_pipeline","VOXEL ART PIPELINE","Game","⭐","Remesh blocks 0.1м, palette quantize, MagicaVoxel exchange"),
(20,"kitbash_greeble","KITBASH GREEBLE CITY","Kitbash","⭐⭐","Greeble GN, kitbash library, decals"),
(21,"motion_graphics_titles","MOTION GRAPHICS TITLES","MoGraph","⭐⭐","Text+GN delay, easing library, alpha over"),
(22,"dataviz_3d_charts","DATAVIZ 3D CHARTS","Info","⭐⭐","CSV→GN bars, color ramp by value, camera path"),
(23,"virtual_production_led","VIRTUAL PRODUCTION LED","VP","⭐⭐⭐","nDisplay config, genlock, camera track, LED wall comp"),
(24,"photogrammetry_cleanup","PHOTOGRAMMETRY CLEANUP","Scan","⭐⭐","RC/Metashape → retopo → bake → LOD → export"),
(25,"ai_concept_to_final","AI CONCEPT→FINAL","AI Pipe","⭐⭐⭐","SD concept → Tripo/Hunyuan 3D → retopo → PBR → render"),
(26,"lookdev_turntable_lab","LOOKDEV TURNTABLE LAB","Lookdev","⭐⭐","HDRI ladder + light ladder + material variants grid"),
(27,"sound_sync_edit","SOUND-SYNC EDIT","Audio","⭐⭐","Audio strips, beat markers, cut on beat, loudness -14 LUFS"),
(28,"localization_dub_titles","LOCALIZATION TITLES","Publish","⭐","SRT import, multi-lang text strips, safe-area check"),
]

CASES = [
(7,"stylized_barrel","STYLIZED BARREL (HAND-PAINT)","Game","⭐⭐","PBR hand-paint, 1.2k tris, Unity export"),
(8,"sci_fi_corridor","SCI-FI CORRIDOR MODULAR","Modular","⭐⭐⭐","Modular kit 2м grid, trim sheets, LOD"),
(9,"anime_head_bust","ANIME HEAD BUST","Character","⭐⭐⭐","Anime proportions, toon shader, shape keys 20"),
(10,"sneaker_product","SNEAKER PRODUCT HERO","Product","⭐⭐","Macro stitching, knit normal, lace curves"),
(11,"cozy_room_diorama","COZY ROOM DIORAMA","Diorama","⭐⭐","10x10см feel, tilt-shift, warm practicals"),
(12,"lowpoly_forest_pack","LOWPOLY FOREST PACK","Environment","⭐⭐","5 trees+bushes+rocks, atlas, wind sway"),
(13,"hard_surface_gun","HARD-SURFACE SCI-FI GUN","Hardsurface","⭐⭐⭐","Bevel weights, boolean, baked normals"),
(14,"food_r visualisation","FOOD RENDER (RAMEN)","Food","⭐⭐","SSS broth, steam sim, condensation drops"),
(15,"car_studio_cinematic","CAR STUDIO CINEMATIC","Automotive","⭐⭐⭐","Studio HDRI rig, paint flakes, turntable"),
(16,"dungeon_tileset","DUNGEON TILESET","Tileset","⭐⭐⭐","2x2м tiles, trim, atlas, Unity grid snap"),
]

def write_setup(num, slug, title, typ, diff, time_, bullets, desc, prompt):
    p = WIKI/"setups"/f"setup_{num:02d}_{slug}.md"
    body = f"""# SETUP {num:02d}: {title}

**ID:** SETUP-{num:02d} | **Type:** {typ} | **Difficulty:** {diff} | **Time:** {time_}
**RU/EN Bilingual**

## 🎯 Цель / Goal
{desc}

## 1. Шаги / Steps
"""
    for i,b in enumerate(bullets,1):
        body += f"{i}. {b}\n"
    body += f"""
## 2. MCP промпт / Prompt
```
{prompt}
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
"""
    p.write_text(body, encoding="utf-8")

def write_wf(num, slug, title, typ, diff, desc):
    p = WIKI/"workflows"/f"wf_{num:02d}_{slug}.md"
    body = f"""# WF {num:02d}: {title}

**ID:** WF-{num:02d} | **Type:** {typ} | **Difficulty:** {diff}
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: {desc}
EN: {desc}

## Этапы / Stages
1. Подготовка / Prep: референсы, масштаб, нейминг
2. Генерация / Generate: MCP tools + Python
3. Материалы/Свет/Камера / Look
4. Рендер/Экспорт / Deliver
5. Проверка / QA

## MCP команды / Commands
```
RU: "Выполни {title} по шагам 1-5 с проверками"
EN: "Run {title} steps 1-5 with checks"
```

## 🔗 Setup 01, Setup 08, INDEX
"""
    p.write_text(body, encoding="utf-8")

def write_case(num, slug, title, typ, diff, desc):
    p = WIKI/"cases"/f"case_{num:02d}_{slug}.md"
    body = f"""# CASE {num:02d}: {title}

**ID:** CASE-{num:02d} | **Type:** {typ} | **Difficulty:** {diff}
**RU/EN Bilingual**

## 🎯 Задача / Brief
RU: {desc}
EN: {desc}

## Чек-лист / Checklist
- [ ] Блокаут/пропорции
- [ ] Топология/UV без ошибок
- [ ] PBR 2k+, нейминг
- [ ] Свет/камера/рендер
- [ ] Экспорт GLB/FBX + превью

## 🔗 WF-07, Setup 01/08, INDEX
"""
    p.write_text(body, encoding="utf-8")

for s in SETUPS:
    write_setup(*s)
for w in WF:
    write_wf(*w)
for c in CASES:
    write_case(*c)
print(f"OK setups={len(SETUPS)} wf={len(WF)} cases={len(CASES)}")
