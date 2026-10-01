# QUALITY REPORT

Автогенерация: `python scripts/quality_report.py`. Не гейт — это бэклог.

Проверяется **наличие секций**, а не язык заголовка: в корпусе два диалекта
(`ЦЕЛЬ/ПРОМПТ/СВЯЗИ` и `GOAL/PROMPT/LINKS`). Эталон структуры: `WIKI/templates/`.

**Файлов с пробелами: 80**

| Категория | Файлов |
|-----------|--------|
| prompts | 2 |
| setups | 48 |
| workflows | 20 |
| cases | 10 |

## По файлам

| Файл | Статус | Не хватает |
|------|--------|-----------|
| `prompts/29_batch_cli.md` | — | mcp |
| `prompts/40_version_control.md` | — | mcp |
| `setups/setup_13_unity_roundtrip.md` | full | links |
| `setups/setup_14_godot_pipeline.md` | full | goal, links |
| `setups/setup_15_comfyui_sdxl.md` | full | goal, links |
| `setups/setup_16_automatic1111_api.md` | stub | goal, links |
| `setups/setup_17_krita_ai_diffusion.md` | stub | goal, links |
| `setups/setup_18_substance_painter_live.md` | full | goal, links |
| `setups/setup_19_substance_designer_sbsar.md` | stub | goal, links |
| `setups/setup_20_zbrush_goz.md` | stub | goal, links |
| `setups/setup_21_marvelous_clo3d.md` | stub | goal, links |
| `setups/setup_22_rizomuv_bridge.md` | stub | goal, links |
| `setups/setup_23_realitycapture_scan.md` | full | goal, links |
| `setups/setup_24_metashape_scan.md` | stub | goal, links |
| `setups/setup_25_polycam_luma.md` | stub | goal, links |
| `setups/setup_26_topogun_quad.md` | stub | goal, links |
| `setups/setup_27_mixamo_autorig.md` | stub | goal, links |
| `setups/setup_28_accurig_cc.md` | stub | goal, links |
| `setups/setup_29_autorignpro.md` | stub | goal, links |
| `setups/setup_30_rigify_advanced.md` | full | goal, links |
| `setups/setup_31_makehuman_mpfb.md` | stub | goal, links |
| `setups/setup_32_daz_diffeomorphic.md` | stub | goal, links |
| `setups/setup_33_cc4_blender.md` | stub | goal, links |
| `setups/setup_34_metahuman_blender.md` | stub | goal, links |
| `setups/setup_35_readyplayerme.md` | stub | goal, links |
| `setups/setup_36_vroid_studio.md` | stub | goal, links |
| `setups/setup_37_blenderkit_assets.md` | stub | goal, links |
| `setups/setup_38_fab_epic.md` | stub | goal, links |
| `setups/setup_39_quixel_bridge.md` | stub | goal, links |
| `setups/setup_40_ambientcg_polyhaven.md` | full | goal, links |
| `setups/setup_41_hdri_lighting_lab.md` | stub | goal, links |
| `setups/setup_42_tripo_ai_api.md` | full | goal, links |
| `setups/setup_43_meshy_api_v4.md` | full | goal, links |
| `setups/setup_44_rodin_hyper3d.md` | full | goal, links |
| `setups/setup_45_hunyuan3d_21.md` | stub | goal, links |
| `setups/setup_46_shap_e_local.md` | stub | goal, links |
| `setups/setup_47_zero123_instantmesh.md` | stub | goal, links |
| `setups/setup_48_gaussian_splatting.md` | stub | goal, links |
| `setups/setup_49_ffmpeg_vse_pipeline.md` | stub | goal, links |
| `setups/setup_50_davinci_roundtrip.md` | stub | goal, links |
| `setups/setup_51_notion_obsidian_docs.md` | stub | goal, links |
| `setups/setup_52_git_lfs_blend.md` | stub | goal, links |
| `setups/setup_53_flamenco_farm.md` | full | goal, links |
| `setups/setup_54_cloud_render_aws.md` | stub | goal, links |
| `setups/setup_55_ai_upscale_pipeline.md` | stub | goal, links |
| `setups/setup_56_mocap_rokoko.md` | full | goal, links |
| `setups/setup_57_face_mocap_arkit.md` | stub | goal, links |
| `setups/setup_58_vr_scene_inspection.md` | stub | goal, links |
| `setups/setup_59_web_viewer_export.md` | stub | goal, links |
| `setups/setup_60_shotgrid_ftrack_sync.md` | stub | goal, links |
| `workflows/wf_09_realtime_vj_loop.md` | stub | goal, links |
| `workflows/wf_10_product_turntable.md` | stub | goal, links |
| `workflows/wf_11_archviz_day_night.md` | stub | goal, links |
| `workflows/wf_12_crowd_sim_gn.md` | stub | goal, links |
| `workflows/wf_13_destruction_rbd.md` | stub | goal, links |
| `workflows/wf_14_cloth_fashion_show.md` | stub | goal, links |
| `workflows/wf_15_fluid_product_splash.md` | stub | goal, links |
| `workflows/wf_16_npr_anime_render.md` | stub | goal, links |
| `workflows/wf_17_stop_motion_felt.md` | stub | goal, links |
| `workflows/wf_18_isometric_game_art.md` | stub | goal, links |
| `workflows/wf_19_voxel_art_pipeline.md` | stub | goal, links |
| `workflows/wf_20_kitbash_greeble.md` | stub | goal, links |
| `workflows/wf_21_motion_graphics_titles.md` | stub | goal, links |
| `workflows/wf_22_dataviz_3d_charts.md` | stub | goal, links |
| `workflows/wf_23_virtual_production_led.md` | stub | goal, links |
| `workflows/wf_24_photogrammetry_cleanup.md` | stub | goal, links |
| `workflows/wf_25_ai_concept_to_final.md` | stub | goal, links |
| `workflows/wf_26_lookdev_turntable_lab.md` | stub | goal, links |
| `workflows/wf_27_sound_sync_edit.md` | stub | goal, links |
| `workflows/wf_28_localization_dub_titles.md` | stub | goal, links |
| `cases/case_07_stylized_barrel.md` | full | links |
| `cases/case_08_sci_fi_corridor.md` | full | links |
| `cases/case_09_anime_head_bust.md` | stub | links |
| `cases/case_10_sneaker_product.md` | stub | links |
| `cases/case_11_cozy_room_diorama.md` | stub | links |
| `cases/case_12_lowpoly_forest_pack.md` | stub | links |
| `cases/case_13_hard_surface_gun.md` | full | links |
| `cases/case_14_food_r visualisation.md` | stub | links |
| `cases/case_15_car_studio_cinematic.md` | stub | links |
| `cases/case_16_dungeon_tileset.md` | stub | links |

## Как закрыть

1. Открыть файл, добавить недостающие секции по образцу `WIKI/templates/`.
2. Прогнать `python scripts/run_all.py`.
3. Проверить: `python scripts/quality_report.py` — число должно уменьшиться.

Когда счётчик станет 0, включайте гейт: `validate.py --strict`.
