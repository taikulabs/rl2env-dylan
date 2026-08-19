**fix(kanban): preserve notifier_profile for dashboard home subscriptions**

Salvages #23947 by @Zyrixtrex.

Preserves notifier_profile on dashboard home-subscribe + backfills ownerless rows; main has notifier_profile column and add_notify_sub takes it, but dashboard plugin_api still omits it.

Cherry-picked onto current main with original authorship preserved via rebase merge.