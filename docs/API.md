# TkvUI API Index (sinh ban-tu-dong — sua tay phan mo ta)

> Tra cuu nhanh theo module. Chi tiet xem source + selftest entry.
> Sinh boi `tools/gen_api.py`-style (xem cuoi file). Quy uoc compiler: xem `docs/TkvUI.Roadmap.md` section 0.

## TkvUI.A11y (`TkvUI.A11y.tkv`)

Accessibility tree model (role/label/value/states/bounds) + UIA/ObjC FFI stubs + JSON dump stub

selftest: `a11y_selftest`

Classes: `A11yNode`

Functions (17): `a11y_role_name`, `a11y_has_action`, `make_a11y_node`, `a11y_bounds_contains`, `a11y_count_children`, `a11y_is_descendant`, `a11y_commit_count`, `a11y_commit`, `a11y_diff_count`, `a11y_win_present`, `a11y_mac_present`, `uia_clients_listening_ex`, `uia_raise_event_ex`, `a11y_macos_class_ex`, `a11y_node_to_json`, `a11y_tree_to_json`, `a11y_dump_json`

## TkvUI.A11yBridge (`TkvUI.A11yBridge.tkv`)

Screen-reader bridge: backend pick UIA/AT-SPI/NS/TalkBack, role/state maps, guarded UIA calls, event router, live regions, providers, reader detect, focus tracker, widget builders, JSON dump that

selftest: `abridge_selftest`

Classes: `AbBridge`, `AbUia`, `AbAtspi`, `AbNs`, `AbTalkback`

Functions (52): `ab_pick_backend`, `ab_backend_name`, `ab_hex_digit`, `ab_char_code`, `ab_json_escape`, `ab_q`, `ab_node_to_json`, `ab_role_uia`, `ab_role_uia_name`, `ab_role_atspi`, `ab_role_ns`, `ab_role_android`, `ab_role_for_backend`, `ab_state_mask`, `ab_state_has`, `ab_state_names`, `ab_uia_state_str`, `ab_uia_listening`, `ab_uia_raise`, `ab_uia_event_id`, `ab_event_name`, `ab_make_bridge`, `ab_log_clear`, `ab_events_json`, `ab_announce`, `ab_poll`, `ab_announce_clear`, `ab_make_uia`, `ab_make_atspi`, `ab_make_ns`, `ab_make_talkback`, `ab_detect_reader`, `ab_reader_confidence`, `ab_reader_name`, `ab_focusables`, `ab_focus_pos`, `ab_focus_next`, `ab_focus_prev`, `ab_add_node`, `ab_add_window`, `ab_add_label`, `ab_add_button`, `ab_add_lineedit`, `ab_add_combo`, `ab_add_listview`, `ab_add_tabs`, `ab_add_dialog`, `ab_add_progress`, `ab_add_slider`, `ab_tree_json_safe`, `ab_dump_tree`, `mv_contains_safe`

## TkvUI.Atspi (`TkvUI.Atspi.tkv`)

AT-SPI provider kieu host-driven: D-Bus envelope + event outbox + tree JSON; SIM cho D-Bus/.so that (upstream)

selftest: `atspi_selftest`

Classes: `AtspiApp`

Functions (18): `atspi_role_name`, `atspi_state_names`, `atspi_event_name`, `atspi_bus_name`, `atspi_msg_register`, `atspi_msg_event`, `atspi_msg_get_role`, `atspi_msg_get_state`, `atspi_make_app`, `atspi_drain`, `atspi_node`, `ab_q_atspi`, `atspi_tree_json`, `atspi_dump_file`, `atspicheck`, `atspicheck_i`, `atspicheck_s`, `mv_contains_safe5`

## TkvUI.Bidi (`TkvUI.Bidi.tkv`)

Bidi UAX#9 + HarfBuzz FFI stub + visual reorder + atlas draw (Hebrew/Arabic/CJK/emoji)

selftest: `bidi_selftest`

Classes: `HbGlyphInfo`, `HbGlyphPosition`, `HbFont`, `HbBuffer`, `BidiCharInfo`, `BidiParagraph`, `BidiRun`, `BidiStackFrame`, `HbShapePlan`

Functions (62): `bidi_get_class`, `bidi_is_strong`, `bidi_is_weak`, `bidi_is_neutral`, `bidi_is_explicit`, `bidi_is_rtl`, `bidi_is_ltr`, `bidi_mirror_char`, `bidi_paragraph_level`, `hb_version_string_ex`, `hb_version_ex`, `hb_buffer_create_ex`, `hb_buffer_destroy_ex`, `hb_buffer_clear_contents_ex`, `hb_buffer_add_utf8_ex`, `hb_buffer_add_utf16_ex`, `hb_buffer_set_direction_ex`, `hb_buffer_set_script_ex`, `hb_buffer_set_language_ex`, `hb_buffer_get_length_ex`, `hb_buffer_get_glyph_infos_ex`, `hb_buffer_get_glyph_positions_ex`, `hb_font_create_ex`, `hb_font_destroy_ex`, `hb_font_set_scale_ex`, `hb_face_create_ex`, `hb_face_destroy_ex`, `hb_blob_create_ex`, `hb_blob_destroy_ex`, `hb_shape_ex`, `hb_script_from_string_ex`, `hb_language_from_string_ex`, `hb_direction_from_string_ex`, `hb_font_from_file`, `hb_shape_text`, `bidi_hb_direction_from_para_level`, `hb_script_from_bidi_class`, `hb_lib_present`, `hb_shape_full`, `hb_shape_run`, `hb_script_for_text`, `hb_shape_plan`, `utf8_seq_range`, `bidi_seq_classes`, `bidi_seq_offset`, `bidi_draw_visual`, `bidi_draw_visual_atlas`, `bidi_process`, `bidi_resolve_explicit`, `bidi_resolve_weak`, `bidi_resolve_neutral`, `bidi_resolve_implicit`, `bidi_reorder`, `bidi_get_visual_runs`, `bidi_classify_all`, `bidi_para_level_of`, `bidi_levels_init`, `bidi_weak_resolve`, `bidi_neutral_resolve`, `bidi_implicit_resolve`

(...+2, xem source)

## TkvUI.Core (`TkvUI.Core.tkv`)

ColorRgba/ColorHsla, Point2D, Rect2D, Matrix3x2, PixelSurface (list[i64]), Theme, Insets/CornerRadius, DPI, SurfacePool-lite

selftest: `core_selftest`

Classes: `ColorRgba`, `Point2D`, `Rect2D`, `Matrix3x2`, `PixelSurface`, `ColorHsla`, `ThemeToken`, `Insets`, `CornerRadius`, `SurfacePoolStats`

Functions (31): `color_from_rgb`, `hex_char_to_val`, `hex_pair_to_int`, `color_from_hex`, `color_lerp`, `matrix_identity`, `matrix_translate`, `matrix_scale`, `matrix_transform_point`, `surface_clear`, `surface_blend_pixel`, `surface_set_pixel`, `surface_fast_blit`, `hue_wrap`, `hue_channel`, `color_from_hsla`, `color_to_hsla`, `theme_default`, `theme_dark`, `theme_light`, `theme_accent`, `theme_radius`, `corner_uniform`, `dp_to_px`, `px_to_dp`, `dpi_scale_for_platform`, `surface_ensure_capacity`, `pool_note_acquire`, `core_check`, `core_check_i`, `core_check_f`

## TkvUI.Data (`TkvUI.Data.tkv`)

Model/View/Delegate: flat cells, filter/sort proxy, MvTableState render, StringList, Text/Spin/Combo/Date delegates

selftest: `data_selftest`

Classes: `MvIndex`, `MvTableState`, `MvStringList`, `MvTextDelegate`, `MvSpinDelegate`, `MvComboDelegate`, `MvDateDelegate`

Functions (30): `make_mv_index`, `mv_invalid`, `mv_flat_idx`, `mv_cell_get`, `mv_cell_set`, `mv_row_append`, `mv_row_remove`, `mv_row_count`, `mv_contains`, `mv_digit_val`, `mv_parse_int`, `mv_is_int`, `mv_compare_str`, `mv_match_cell`, `mv_filter_apply`, `mv_visible_to_real`, `mv_visible_count`, `mv_sort_build`, `make_mv_table`, `make_mv_stringlist`, `make_mv_text_delegate`, `make_mv_spin_delegate`, `make_mv_combo_delegate`, `make_mv_date_delegate`, `mvcheck`, `mvcheck_i`, `mvcheck_s`, `mv_seed_cells`, `mv_seed_order`, `mv_seed_visible`

## TkvUI.Effects (`TkvUI.Effects.tkv`)

box_blur, kawase_blur 3-pass, backdrop_blur (glass), specular highlight, drop shadow

selftest: `effects_selftest`

Functions (14): `apply_box_blur`, `draw_specular_highlight`, `draw_drop_shadow`, `box_blur_pass_ref`, `box_blur_pass`, `kawase_blur`, `half_res_blur`, `backdrop_blur`, `effects_check`, `effects_check_i`, `effects_check_gt`, `effects_pixel_r`, `effects_count_bright`, `effects_check_ge_int`

## TkvUI.Events (`TkvUI.Events.tkv`)

PointerEventArgs, HitTestResult, pointer_button_label, no_hit

selftest: `(khong co — data-only)`

Classes: `PointerEventArgs`, `HitTestResult`

Functions (2): `pointer_button_label`, `no_hit`

## TkvUI.Font (`TkvUI.Font.tkv`)

Windows GDI font baker (CreateFontA+TextOutA vao DIB, GetPixel ve atlas alpha coverage), font_measure/draw_string. Optional, khong import boi umbrella (can GDI that).

selftest: `font_selftest`

Classes: `FontHandle`

Functions (15): `font_charset`, `font_cell_w`, `font_cell_h`, `font_font_px`, `font_cols`, `font_atlas_w`, `font_atlas_h`, `font_rows_needed`, `font_build_dib_info`, `font_create`, `font_measure`, `font_draw_string`, `font_check`, `font_check_i`, `font_check_gt`

## TkvUI.FontFallback (`TkvUI.FontFallback.tkv`)

Chuoi font du phong: Text 5x7 -> Viet 134 glyph -> i18n baked (Hebrew/Arabic/CJK) -> box fallback; monospace 6px/seq

selftest: `fallback_selftest`

Functions (17): `fb_classify`, `fb_font_name`, `fb_advance`, `fb_measure`, `fb_count_missing`, `fb_has_font`, `fb_resolve`, `fb_draw_run_viet`, `fb_draw_run_i18n`, `fb_draw_run_box`, `fb_draw_string`, `fbcheck`, `fbcheck_i`, `fbcheck_f`, `fbcheck_s`, `fb_oracle`, `fb_candidates`

## TkvUI.Gpu (`TkvUI.Gpu.tkv`)

GPU abstraction + factory + backend pick + Vulkan/D3D11/Metal probes + shader pipeline stubs

selftest: `gpu_selftest`

Classes: `GpuBackend`, `ShaderModule`, `PipelineLayout`, `GraphicsPipeline`, `ComputePipeline`

Functions (48): `gpu_backend_name`, `gpu_backend_kind_valid`, `gpu_pick_backend`, `gpu_is_nvidia_vendor`, `gpu_vendor_name`, `make_software_backend`, `make_vulkan_backend`, `make_metal_backend`, `gpu_create_best`, `gpu_vulkan_present`, `gpu_metal_present`, `vk_loader_present`, `vk_proc_addr`, `vk_create_instance_ex`, `vk_destroy_instance_ex`, `vk_enumerate_devices_ex`, `mtl_get_class_ex`, `mtl_sel_register_ex`, `vk_physical_device_get_queue_family`, `vk_instance_create`, `vk_instance_destroy`, `vk_physical_device_select`, `vk_device_create`, `vk_device_destroy`, `vk_swapchain_create`, `vk_swapchain_destroy`, `vk_swapchain_present`, `vk_queue_submit`, `vk_command_pool_create`, `vk_command_buffer_allocate`, `vk_render_pass_create`, `vk_framebuffer_create`, `vk_pipeline_create`, `shader_module_create`, `shader_module_destroy`, `pipeline_layout_create`, `pipeline_layout_destroy`, `graphics_pipeline_create`, `graphics_pipeline_destroy`, `compute_pipeline_create`, `compute_pipeline_destroy`, `d3d11_device_create`, `d3d11_swap_chain_create`, `d3d11_shader_compile`, `metal_device_create_default`, `metal_library_create`, `metal_function_create`, `metal_render_pipeline_create`

## TkvUI.Graphics (`TkvUI.Graphics.tkv`)

draw_line (Bresenham), fill/stroke_round_rect, draw_arc (Sin/Cos), draw_polyline, clip_rect_intersect, draw_image

selftest: `graphics_selftest`

Functions (14): `draw_line`, `fill_round_rect`, `stroke_round_rect`, `draw_arc`, `draw_polyline`, `clip_rect_intersect`, `draw_image`, `graphics_count_nonzero`, `graphics_check`, `graphics_check_i`, `graphics_check_f`, `graphics_pixel_r`, `graphics_pixel_alpha`, `graphics_row_count`

## TkvUI.I18nData (`TkvUI.I18nData.tkv`)

Baked subset font bytes (Hebrew/Arabic/CJK) + codepoint/slot tables cho text_atlas_bake_i18n (khong doc file luc chay)

selftest: `(khong co — data-only)`

Functions (6): `i18n_cps_he`, `i18n_cps_cjk`, `i18n_codepoint`, `i18n_slot_for`, `i18n_font_bytes_he`, `i18n_font_bytes_cjk`

## TkvUI.Ime (`TkvUI.Ime.tkv`)

Bo go Tieng Viet Telex/VNI + composition state; tone/mu/breve/horn; composer thuan logic + OS stub; SIM cho IME that

selftest: `ime_selftest`

Classes: `ImeBuffer`

Functions (31): `ime_is_vowel`, `ime_base_vowel`, `ime_apply_tone`, `ime_apply_hat`, `ime_telex_tone`, `ime_vni_tone`, `ime_apply_tone_up`, `ime_apply_hat_up`, `ime_tone_of`, `ime_hat_of`, `ime_bare_vowel`, `ime_last_start`, `ime_last_seq`, `ime_drop_last`, `ime_tone_hat`, `ime_push_telex`, `ime_push_vni`, `ime_push`, `ime_backspace`, `ime_type_word`, `ime_make_buffer`, `ime_os_get_composition`, `ime_os_notify`, `ime_os_present`, `imecheck`, `imecheck_s`, `imecheck_i`, `ime_keys2`, `ime_keys3`, `ime_keys5`, `ime_keys6`

## TkvUI.Input (`TkvUI.Input.tkv`)

hit_test_tree topmost-first, EventDispatcher (pointer capture), TouchEventArgs, GestureRecognizer (tap/pan/pinch)

selftest: `input_selftest`

Classes: `TouchEventArgs`, `GestureEvent`, `GestureRecognizer`, `EventDispatcher`

Functions (11): `input_event_name`, `gesture_name`, `input_dist`, `hit_test_tree`, `hit_test_rect`, `make_touch`, `make_gesture_recognizer`, `make_dispatcher`, `input_check`, `input_check_str`, `input_check_f`

## TkvUI.Layout (`TkvUI.Layout.tkv`)

FlexStyle/GridStyle/Constraint, flex row/col wrap + cross-align + justify, stack, grid + span, DPI, validator

selftest: `layout_selftest`

Classes: `FlexStyle`, `GridStyle`, `Constraint`

Functions (28): `flex_style`, `grid_style`, `constraint`, `layout_clamp`, `constraint_w`, `constraint_h`, `layout_dp`, `layout_dp_i`, `flex_line_count`, `flex_lines_increasing`, `flex_same_line_same_cross`, `flex_no_overlap`, `flex_within_bounds`, `layout_flex_row`, `layout_flex_col`, `layout_flex`, `layout_stack_row`, `layout_stack_col`, `layout_stack`, `layout_grid_cell`, `layout_grid`, `layout_measure_total`, `layout_alloc_f64`, `layout_alloc_i32`, `layout_check`, `layout_check_i`, `layout_check_f`, `layout_selftest_screen`

## TkvUI.Media (`TkvUI.Media.tkv`)

Media-player UI: transport, seekbar, volume, repeat, shuffle, speed, playlist, equalizer+presets, spectrum, A-B loop, media_format_time

selftest: `media_selftest`

Classes: `MediaTransportWidget`, `MediaSeekBarWidget`, `MediaVolumeWidget`, `MediaRepeatWidget`, `MediaShuffleWidget`, `MediaSpeedWidget`, `MediaPlaylistWidget`, `MediaEqualizerWidget`, `MediaSpectrumWidget`, `MediaABLoopWidget`

Functions (20): `media_format_time`, `media_list_count_f`, `media_list_count_s`, `media_count_non_bg`, `make_media_transport`, `make_media_seekbar`, `make_media_volume`, `make_media_repeat`, `make_media_shuffle`, `make_media_speed`, `make_media_playlist`, `make_media_equalizer`, `media_eq_preset_value`, `media_eq_apply_preset`, `make_media_spectrum`, `make_media_abloop`, `media_check`, `media_check_i`, `media_check_f`, `media_check_ge`

## TkvUI.NativeDlg (`TkvUI.NativeDlg.tkv`)

File/Color/Font dialogs (API day du, stub cho Win32 that); filter/path/color/hex/font; render browser; SIM cho native marshal

selftest: `nativedlg_selftest`

Classes: `DlgFile`, `DlgColor`, `DlgFont`

Functions (34): `dlg_parse_filter`, `dlg_match_star`, `dlg_match_list`, `dlg_parent`, `dlg_join`, `dlg_basename`, `dlg_ext`, `dlg_make_open`, `dlg_make_save`, `dlg_make_dir`, `dlg_make_color`, `dlg_hex_digit`, `dlg_hex2`, `dlg_hexval`, `dlg_pack`, `dlg_unpack_r`, `dlg_unpack_g`, `dlg_unpack_b`, `dlg_custom_add`, `dlg_custom_get`, `dlg_make_font`, `dlg_native_open`, `dlg_native_save`, `dlg_native_dir`, `dlg_native_color`, `dlg_native_font`, `dlg_native_present`, `dlg_render_browser`, `dlgcheck`, `dlgcheck_i`, `dlgcheck_s`, `dlg_seed_names`, `dlg_seed_dirs`, `dlg_alloc`

## TkvUI.Platform (`TkvUI.Platform.tkv`)

detect_platform() thật (probe runtime), Win32 ULW thật, X11/Cocoa stub, Android/iOS host-driven contract

selftest: `platform_selftest`

Classes: `PlatformWindowHandle`, `Win32Platform`, `X11Platform`, `CocoaPlatform`, `AndroidPlatform`, `IOSPlatform`

Functions (85): `tkv_has_env`, `tkv_has_file`, `ime_get_context`, `ime_release_context`, `ime_get_composition_string`, `ime_set_composition_string`, `ime_notify_ime`, `detect_platform_id`, `detect_platform`, `win_last_error`, `win_write_u32_le`, `win_build_dib_info`, `wf_create`, `wf_show`, `wf_hide`, `wf_close`, `wf_set_title`, `wf_set_opacity`, `wf_refresh`, `wf_backend_name`, `wf_get_handle`, `wf_set_parent`, `wf_set_bounds`, `wf_get_bounds`, `wf_invalidate`, `wf_do_events`, `wf_run`, `wf_exit`, `wf_create_control`, `wf_add_control`, `wf_remove_control`, `wf_set_text`, `wf_get_text`, `wf_set_visible`, `wf_set_enabled`, `wf_set_font`, `wf_set_color`, `wf_set_dock`, `wf_set_anchor`, `wf_subscribe_click`, `wf_subscribe_text_changed`, `wf_subscribe_value_changed`, `wf_subscribe_form_closing`, `win_poll_messages`, `win_pointer_x`, `win_pointer_y`, `win_key_down`, `win_has_dpi_api`, `win_dpi_for_window`, `win_system_dpi`, `win_dpi_scale`, `win_window_dpi_scale`, `win_dpi_changed`, `win_dpi_ack`, `win_user_lang`, `win_is_rtl_lang`, `win_is_rtl`, `android_copy_pixels`, `make_android_platform`, `ios_sel_register_name`

(...+25, xem source)

## TkvUI.Printing (`TkvUI.Printing.tkv`)

In/PDF thuan .tkv: PdfPaper/Printer/Margins, PdfFont Base14, PdfPainter (text/rect/path), PdfDocument+xref, table export, PrintDialog stub, PrintPreview

selftest: `printing_selftest`

Classes: `PdfPaper`, `PdfMargins`, `PdfPrinter`, `PdfFont`, `PdfPainter`, `PdfDocument`, `PrintDialog`, `PrintPreview`

Functions (71): `pdf_paper_a4`, `pdf_paper_a5`, `pdf_paper_letter`, `pdf_paper_legal`, `pdf_paper_a3`, `pdf_paper_custom`, `pdf_paper_for_kind`, `pdf_margins_normal`, `pdf_margins_narrow`, `pdf_margins_wide`, `pdf_make_printer`, `pdf_mm_to_pt`, `pdf_pt_to_mm`, `pdf_inch_to_pt`, `pdf_font_helvetica`, `pdf_font_bold`, `pdf_font_times`, `pdf_font_courier`, `pdf_text_width`, `pdf_text_width_mono`, `pdf_font_embed`, `pdf_line_height`, `pdf_sanitize`, `pdf_escape`, `pdf_num`, `pdf_make_painter`, `pdf_op_save`, `pdf_op_restore`, `pdf_op_stroke_rgb`, `pdf_op_fill_rgb`, `pdf_op_line_w`, `pdf_op_line`, `pdf_op_rect`, `pdf_op_text`, `pdf_op_text_center`, `pdf_op_text_right`, `pdf_op_placeholder`, `pdf_ops_join`, `pdf_make_doc`, `pdf_add_page`, `pdf_pad10`, `pdf_font_obj`, `pdf_build`, `pdf_save`, `pdf_load_head`, `pdf_export_table`, `print_make_dialog`, `print_dialog_native`, `print_make_preview`, `pdf_op_poly`, `pdf_op_circle`, `pdf_op_clip_rect`, `pdf_face_factor`, `pdf_face_ascent`, `pdf_face_descent`, `pdf_text_width_face`, `pdf_font_box`, `pdf_fit_size`, `pdf_col_autowidth`, `pdf_printer_summary`

(...+11, xem source)

## TkvUI.SQLite (`TkvUI.SQLite.tkv`)

SQL/ORM in-memory thuan .tkv: schema phang, CRUD, snapshot transaction, SqlTableModel (Data proxy), SqlQuery cursor, SqlRelation

selftest: `sqlite_selftest`

Classes: `SqlColumn`, `SqlDb`, `SqlTableModel`, `SqlQuery`, `SqlRelation`

Functions (44): `make_sql_column`, `make_sql_column_nn`, `make_sql_db`, `sql_open`, `sql_close`, `sql_is_open`, `sql_table_idx`, `sql_table_ncol`, `sql_col_pos`, `sql_col_flag`, `sql_create_table`, `sql_set_notnull`, `sql_seg_start`, `sql_rebase`, `sql_shift_right`, `sql_shift_left`, `sql_insert`, `sql_row_get`, `sql_row_set`, `sql_match_row`, `sql_select`, `sql_update_rows`, `sql_delete_rows`, `sql_count_rows`, `sql_sum_int`, `sql_snap_copy`, `sql_snap_copy_i`, `sql_begin`, `sql_commit`, `sql_rollback`, `make_sql_tablemodel`, `sql_model_project`, `sql_model_refresh`, `sql_model_cell`, `make_sql_query`, `make_sql_relation`, `sql_relation_label`, `sqlcheck`, `sqlcheck_i`, `sqlcheck_s`, `sql_cols2`, `sql_cols4`, `sql_types2`, `sql_types4`

## TkvUI.Text (`TkvUI.Text.tkv`)

Font bitmap 5x7 (95 glyph + box fallback), glyph atlas pre-baked (text_atlas_draw_string), char_code, measure_string, draw_string (align/tracking/scale), wrap + ellipsis

selftest: `text_selftest`

Classes: `TextMetrics`, `GlyphAtlas`, `TtfFont`

Functions (62): `text_charset`, `char_code`, `glyph_width`, `atlas_width_for`, `atlas_rows_needed`, `atlas_make_record`, `atlas_create`, `atlas_buffer`, `atlas_glyph_origin`, `atlas_bake`, `atlas_blit_glyph`, `glyph_pattern`, `measure_string`, `draw_string`, `text_atlas_draw_string`, `text_atlas_make`, `text_atlas_record`, `text_atlas_baked_buffer`, `text_line_count`, `measure_block`, `draw_text_block`, `bit1`, `bit2`, `bit4`, `bit8`, `bit16`, `bit32`, `ttf_read_u16`, `ttf_read_i16`, `ttf_read_u32`, `ttf_read_tag`, `ttf_parse_head`, `ttf_parse_hhea`, `ttf_parse_hmtx`, `ttf_find_table`, `ttf_parse_cmap_format4`, `ttf_parse_cmap`, `ttf_char_to_glyph`, `ttf_parse_glyf`, `ttf_bezier_eval`, `ttf_flatten_quad`, `ttf_rasterize_glyph`, `ttf_load_font`, `ttf_get_glyph_metrics`, `ttf_get_glyph_id`, `ttf_rasterize_glyph_to_atlas`, `ttf_atlas_bake`, `text_atlas_bake_i18n`, `text_atlas_record_i18n`, `text_atlas_bake_i18n_all`, `text_atlas_draw_i18n`, `font_family_resolve`, `text_draw_fallback`, `ttf_put_u16`, `ttf_put_u32`, `ttf_test_font_bytes`, `text_check`, `text_check_i`, `text_check_i64`, `text_check_f`

(...+2, xem source)

## TkvUI.Theme (`TkvUI.Theme.tkv`)

OS native-look theme engine: OsPalette 13 roles (Light/Dark/HighContrast), OsMetrics, OsTheme state, state-derivation + geometry helpers

selftest: `theme_selftest`

Classes: `OsPalette`, `OsMetrics`, `OsTheme`, `OsAnim`

Functions (70): `os_palette_light`, `os_palette_dark`, `os_palette_highcontrast`, `os_palette_for_mode`, `os_role_color`, `os_mix_channel`, `os_state_color`, `os_button_bg`, `os_button_fg`, `os_edit_bg`, `os_edit_border`, `os_row_bg`, `os_row_fg`, `os_header_bg`, `os_tooltip_bg`, `os_tooltip_fg`, `os_focus_color`, `os_link_color`, `os_metrics_default`, `os_metrics_scaled`, `os_metrics_for_dpi`, `os_theme_make`, `os_theme_palette`, `os_theme_metrics`, `os_theme_apply_mode`, `os_theme_is_dark`, `os_theme_is_rtl`, `os_button_size`, `os_scrollbar_thumb`, `os_scrollbar_thumb_pos`, `os_progress_fill`, `os_slider_ratio`, `os_slider_value`, `os_tab_cell_w`, `os_tab_hit`, `os_list_first_visible`, `os_list_visible_count`, `os_clamp_scroll`, `os_dialog_button_w`, `os_split_clamp`, `os_anim_make`, `os_anim_open`, `os_anim_ease`, `os_anim_lerp`, `os_anim_hover_state`, `os_mirror_x`, `os_mirror_rect`, `os_apply_rtl`, `os_separator_color`, `os_disabled_text`, `os_menu_bg`, `os_menu_fg`, `os_menu_fg_fixed`, `os_tab_bg`, `os_tab_fg`, `os_progress_bg`, `os_progress_chunk`, `os_slider_groove`, `os_slider_handle`, `os_spin_button_w`

(...+10, xem source)

## TkvUI.Uia (`TkvUI.Uia.tkv`)

UIA provider kieu host-driven: fragment JSON + event outbox + live regions; SIM cho COM vtable that (upstream)

selftest: `uia_selftest`

Classes: `UiaProvider`

Functions (23): `uia_pattern_for_role`, `uia_pattern_name`, `uia_toggle_state`, `uia_expand_state`, `uia_first_child`, `uia_last_child`, `uia_parent_of`, `uia_next_sibling`, `uia_prev_sibling`, `uia_navigate`, `uia_make_provider`, `uia_frag_node`, `uia_frag_json`, `uia_outbox_push`, `uia_outbox_pop`, `uia_outbox_clear`, `uia_dump_file`, `uiacheck`, `uiacheck_i`, `uiacheck_s`, `uia_seed_ids`, `uia_seed_parents`, `mv_contains_safe4`

## TkvUI.Viet (`TkvUI.Viet.tkv`)

Vietnamese bitmap 5x7 (134 precomposed glyphs), UTF-8 sequence utils (vi_strlen/vi_seq_len_at/vi_truncate), vi_draw_bits

selftest: `(khong co — data-only)`

Functions (8): `vi_bits`, `vi_row_of`, `vi_is_ascii`, `vi_seq_len_at`, `vi_strlen`, `vi_truncate`, `vi_draw_bits`, `utf8_seq_len`

## TkvUI.Widgets.Native (`TkvUI.Widgets.Native.tkv`)

16 native-look widgets (Button/LineEdit/ComboBox/Table/Tree/TabBar/MenuBar/ToolBar/Dialog/ScrollBar/Splitter/Progress/Slider/SpinBox/ListView/ToolTip)

selftest: `native_selftest`

Classes: `NativeButton`, `NativeLineEdit`, `NativeComboBox`, `NativeTableView`, `NativeTreeView`, `NativeTabBar`, `NativeMenuBar`, `NativeToolBar`, `NativeDialog`, `NativeScrollBar`, `NativeSplitter`, `NativeProgressBar`, `NativeSlider`, `NativeSpinBox`, `NativeListView`, `NativeToolTip`

Functions (25): `make_native_button`, `make_native_button_default`, `make_native_check`, `make_native_lineedit`, `make_native_password`, `make_native_combo`, `make_native_table`, `make_native_tree`, `make_native_tabs`, `make_native_tabs_closable`, `make_native_menubar`, `make_native_toolbar`, `make_native_dialog`, `make_native_dialog_buttons`, `make_native_scrollbar`, `make_native_splitter`, `make_native_progress`, `make_native_slider`, `make_native_spinbox`, `make_native_listview`, `make_native_tooltip`, `nvcheck`, `nvcheck_i`, `nvcheck_f`, `nv_widths`

## TkvUI.Widgets (`TkvUI.Widgets.tkv`)

UIElement + 28 widget (15 base + DPad/ControlBtn/Joystick + 10 Ant-inspired), Spring/Tween, InvalidationManager, FrameScheduler, RenderLoop

selftest: `widget_selftest`

Classes: `SpringParams`, `SpringAnimation`, `Tween`, `InvalidationManager`, `FrameScheduler`, `UIElement`, `ButtonWidget`, `TextInputWidget`, `CardWidget`, `MetricRingWidget`, `ProgressBarWidget`, `SwitchWidget`, `SliderWidget`, `TextFieldWidget`, `ListViewWidget`, `TabsWidget`, `DialogWidget`, `ToastWidget`, `ChartSparklineWidget`, `BottomSheetWidget`, `NavBarWidget`, `SplitViewWidget`, `DirectionalPadWidget`, `ControlButtonWidget`, `VirtualJoystickWidget`, `AntTagWidget`, `AntBadgeWidget`, `AntAvatarWidget`, `AntAlertWidget`, `AntPaginationWidget`, `AntStepsWidget`, `AntTableWidget`, `AntSelectWidget`, `AntRateWidget`, `AntSpinWidget`, `RenderLoop`, `FocusManager`

Functions (54): `spring_new`, `ease_linear`, `ease_out_cubic`, `ease_in_out_cubic`, `ease_out_back`, `ease_apply`, `tween_to`, `make_invalidation`, `make_frame_scheduler`, `make_button`, `make_button_outline`, `make_textinput`, `make_card`, `make_card_notch`, `make_metric_ring`, `make_progress`, `make_switch`, `make_slider`, `make_textfield`, `empty_textfield`, `make_listview`, `make_tabs`, `make_dialog`, `make_toast`, `make_sparkline`, `make_bottom_sheet`, `make_navbar`, `make_split_view`, `make_dpad`, `make_control_btn`, `make_joystick`, `ant_str_count`, `ant_tag_color`, `make_ant_tag`, `make_ant_badge`, `make_ant_dot`, `make_ant_avatar`, `ant_alert_color`, `make_ant_alert`, `make_ant_pagination`, `make_ant_steps`, `make_ant_table`, `make_ant_select`, `make_ant_rate`, `make_ant_spin`, `make_render_loop`, `render_loop_pump_all`, `widget_row_labels`, `widget_sample_values`, `widget_count_non_bg`, `widget_count_changed`, `widget_check`, `widget_check_i`, `widget_check_ge`

---
Tong: 27 modules, 142 classes, 916 functions.
