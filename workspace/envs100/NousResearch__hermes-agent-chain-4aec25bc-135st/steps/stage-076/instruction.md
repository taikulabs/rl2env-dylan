**fix(tui): improve Charizard completion menu contrast**

Salvage of #28205 by @houenyang-momo.

**What:** The Charizard skin's completion menu used the same dim ember tones for background and dim text, producing poor contrast on dark terminals. Banner-dim was also too dark (`#7A3511`) against banner-text.

**How:** Add explicit dark-ember completion menu colors (`completion_menu_bg`, `completion_menu_current_bg`, `completion_menu_meta_bg`, `completion_menu_meta_current_bg`, `selection_bg`) and lift `banner_dim` to `#C58A45`. Test asserts the new colors load from the skin definition.

Original PR: