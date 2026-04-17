# NAV Audit

Stand: 2026-03-03

## Renderer-Ansatz

- Die Navbar wird zentral ueber `app/nav.py` mit `build_nav_items(user)` erzeugt.
- `base.html` rendert nur noch eine einzige Schleife ueber `get_nav_items(current_user)`.
- GET-Links werden als `<a>` und POST-Links (Logout) als `<form method="post">` mit CSRF gerendert.

## Rollenmatrix

| Rolle | Linktext-Key | Route | Methode |
|---|---|---|---|
| guest | `nav.discover` | `/` | GET |
| guest | `nav.submit` | `/submit` | GET |
| guest | `nav.login` | `/login` | GET |
| guest | `nav.register` | `/register` | GET |
| user | `nav.discover` | `/` | GET |
| user | `nav.submit` | `/submit` | GET |
| user | `nav.my_submissions` | `/my-submissions` | GET |
| user | `nav.favorites` | `/favorites` | GET |
| user | `nav.profile` | `/me` | GET |
| user | `nav.logout` | `/logout` | POST |
| admin | `nav.discover` | `/` | GET |
| admin | `nav.publish_recipe` | `/recipes/new` | GET |
| admin | `nav.admin` | `/admin` | GET |
| admin | `nav.admin_submissions` | `/admin/submissions` | GET |
| admin | `nav.profile` | `/me` | GET |
| admin | `nav.logout` | `/logout` | POST |

## Redundanz-Befund

1. Der Admin-Link `Rezept einreichen` (`/submit`) wurde aus der Admin-Navigation entfernt.
2. Admin nutzt jetzt eindeutig `Rezept veroeffentlichen` (`/recipes/new`) fuer direkte Veroeffentlichung.
3. Die alte Rollen-`if/elif`-Linkverdrahtung in `base.html` wurde durch eine zentrale Nav-Datenstruktur ersetzt.

