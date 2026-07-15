# Quill — Product Specification

One hundred product and UX improvements, planned as a product manager and
designer would: grouped by the moment in the user journey they serve, each
one small enough to verify and large enough to matter.

Status legend: ✅ shipped · 🔜 planned (designed here, not yet built)

## A. Writing & publishing (the author's desk)

1. ✅ Live word & character count in the editor
2. ✅ Save draft with ⌘/Ctrl+S
3. ✅ Unsaved-changes warning before leaving the editor
4. ✅ Tag input as removable chips (comma/Enter to add)
5. ✅ Publish confirmation sheet (review title, subtitle, tags before going live)
6. ✅ Focus mode — hide all chrome except the canvas
7. ✅ Autosave status indicator ("Saved 12s ago")
8. ✅ Editor toolbar: headings, bold/italic, quote, code, lists, link
9. ✅ Draft preview links — share a secret URL of an unpublished draft
10. ✅ Unlisted stories — published but hidden from feeds; readable by link
11. ✅ Pin a story to the top of your profile
12. ✅ Cover image picker with replace/remove states
13. ✅ Subtitle field with live length budget
14. ✅ Quick publish/unpublish from the drafts list
15. ✅ Last-edited relative timestamps on drafts
16. ✅ Word count surfaced on every story (API + dashboard)

## B. Reading experience (the reader's chair)

17. ✅ Reading progress bar
18. ✅ Auto table of contents with scroll-position highlighting
19. ✅ Adjustable article text size (S/M/L, persisted)
20. ✅ Image lightbox — click any article image to view full-screen
21. ✅ Copy button on code blocks
22. ✅ Article links open safely in a new tab
23. ✅ Drop caps and editorial typography
24. ✅ Reading-time estimate on every story
25. ✅ View counts (author's own views excluded)
26. ✅ "Keep reading" — related stories by tag/category
27. ✅ "More from this author" rail on every story
28. ✅ Comment-count link in the byline that jumps to the conversation
29. ✅ Back-to-top button on long reads
30. ✅ Print stylesheet — articles print clean, chrome-free
31. 🔜 Remember scroll position when returning to a story
32. ✅ Serif display + humanist body type pairing

## C. Conversation (comments)

33. ✅ Threaded replies
34. ✅ Comment editing with "(edited)" marker
35. ✅ Comment likes with liked-state
36. ✅ @mentions in comments notify the mentioned writer
37. ✅ Sort conversation by newest or most loved
38. ✅ Collapse long reply threads ("show N replies")
39. ✅ ⌘/Ctrl+Enter posts a comment
40. ✅ Character budget indicator as you approach the limit
41. ✅ Relative timestamps ("3h ago") with exact time on hover
42. ✅ Confirm dialog before deleting a comment

## D. Identity & community

43. ✅ Follow writers; follower/following counts
44. ✅ Following feed
45. ✅ Verified-writer badge (granted by admins)
46. ✅ Rich profiles: bio, website, X, GitHub, location, joined date
47. ✅ Pinned story shown first on profiles
48. ✅ Follower / following lists (viewable)
49. ✅ Share-profile button (copy link)
50. ✅ Who-liked list on stories
51. ✅ Avatar upload with deterministic colored-initial fallback
52. ✅ Remove avatar (revert to initials)
53. 🔜 Mute a writer (hide from your feeds without unfollowing)

## E. Discovery

54. ✅ Site-wide search across stories and writers
55. ✅ Search operators: `author:name` and `tag:name`
56. ✅ Recent searches (kept locally, one-tap re-run)
57. ✅ Matched-term highlighting in results
58. ✅ Topics index with type-scaled tag cloud
59. ✅ Filter box on the topics page
60. ✅ Editors' picks — featured stories curated by admins
61. ✅ Trending / Most-loved / Latest feed tabs
62. ✅ Load more — paginated feed without reloading
63. ✅ Reading history — recently viewed stories, clearable
64. ✅ Per-author RSS feeds (/rss/{username}.xml)
65. ✅ Global RSS + sitemap
66. ✅ JSON-LD Article structured data for search engines
67. ✅ Canonical URLs + absolute OpenGraph images

## F. Notifications

68. ✅ Real-time notifications over WebSocket
69. ✅ Typed notifications: like / comment / follow / mention / system
70. ✅ Per-type notification preferences
71. ✅ Filter notifications by unread / type
72. ✅ Clear-all notifications
73. ✅ Unread badge with 9+ cap
74. ✅ Deep-link: tapping a notification opens the story/profile

## G. Trust, safety & account

75. ✅ Report a story or comment (with reason)
76. ✅ Admin reports queue with resolve action
77. ✅ Session list — see your active devices
78. ✅ Revoke any of your own sessions
79. ✅ Export your data (JSON of profile, stories, comments)
80. ✅ Delete your account (password-confirmed, soft-delete + token revocation)
81. ✅ Password change with strength meter at registration
82. ✅ Auth tokens auto-refresh — no silent logouts mid-session

## H. Interface & polish

83. ✅ Command palette (⌘K): search, navigate, switch theme
84. ✅ Toast notifications for every action, with undo for bookmarks
85. ✅ Confirm dialogs for all destructive actions
86. ✅ Three-way theme: light / dark / follow system
87. ✅ Theme toggle in navbar and settings
88. ✅ Skeleton loading states for every route
89. ✅ Designed empty states (feed, drafts, bookmarks, search, notifications)
90. ✅ Friendly error and 404 pages
91. ✅ Mobile navigation menu
92. ✅ Scroll-aware navbar (gains a shadow when the page scrolls)
93. ✅ Skip-to-content link for keyboard users
94. ✅ Visible focus rings throughout
95. ✅ Reduced-motion support
96. ✅ Like-button micro-animation
97. ✅ Greeting header for signed-in readers ("Good morning, amara")
98. ✅ Dashboard table column sorting + view-share mini bars
99. ✅ Web app manifest + themed favicon
100. ✅ ESC closes every menu, modal, and palette

## Deliberately deferred

- Scheduled publishing (needs a job runner to be honest about semantics)
- Email digests (no mail infrastructure)
- Post revision history (heavy storage model; revisit with demand)
