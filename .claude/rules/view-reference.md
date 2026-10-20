---
paths:
  - "src/audio-start/AudioStar.Desktop/Views/**"
  - "src/audio-start/AudioStar.Desktop/ViewModels/**"
  - "src/audio-start/AudioStar.Desktop/Resources/**"
---

# Reference view: the YouTube page

The YouTube source page (`Views/SourceView.xaml`, `ViewModels/SourceViewModel.cs`) is the approved layout and design, settled with the owner on 2026-10-19. When another view is restyled, it adopts these patterns; a view-specific deviation needs the owner's word.

The owner's principle, in their words: "a very clean, decent layout, with the blue as indication where the action is ... smartly using available space". Every rule below serves one of those three: quiet neutral surfaces and hairlines, blue only where something can be done or is playing, and panes, cards and columns that fill the width instead of leaving empty space.

## Layout

- Page grid margin `{StaticResource PageMargin}` (`28,22,28,12`; `PageMarginRoomy` `28,22,28,22` where the whole page scrolls); header rows, then one `*` row for content.
- Equal side margins: the outermost content (text, fields, hairlines, cards, rows, buttons) ends as far from the window's right edge as it starts from the sidebar divider, 28 DIP (42 px at 150 percent). A `ScrollViewer` or `ListView` takes `Margin="{StaticResource ScrollGutter}"` (`0,0,-10,0`; `ScrollGutterBelow10` and `ScrollGutterBelow14` add a top gap) so its scrollbar sits inside the right margin, and its content keeps a right inset of 10. Header actions outside the scroller (Save, icon actions) end on the same right edge.
- Header: the page title (`PageTitle`) alone on its row. No hint, cookie or status lines under it; connection state lives in the sidebar switches, not on the page.
- Input row: a full-width `TextBox` (column `*`) with its hint text inside the box (a `TextBlock` overlay, `IsHitTestVisible="False"`, margin `11,0,0,0`) and the action button in an `Auto` column after it (`Margin="8,0,0,0"`, `VerticalAlignment="Center"`). Never a fixed-width box, never a label column in front of it. The owner's word for every page: "i prefere full width". Search boxes with no button (My Music, Radio, Enter still searches) and a selector with an icon action (Home Share's server `ComboBox` with "Media server" inside and Up at the end) follow the same row.
- Two panes: master `*` (MinWidth 180), an 18 px divider column, detail `2*` (MinWidth 320). The divider is a `HairlineSplitter` the user drags.
- Master pane: a `ScrollViewer` whose content has a right margin of 10 so the scrollbar never covers cards; a `SectionTitle`, then the cards.
- Detail pane: a header `DockPanel` (title left, the primary action right, `Margin="0,18,0,8"`), a column header row, then the list.

## Components

- Buttons: every text button uses the implicit accent style (blue, white text, min width 100, no per-button padding or width). Icon, transport and card buttons keep `IconButton`, `PlayButton`, `CardButton`. The track pane's list/card toggle, left of "Play all", is an accent-filled button with a white glyph at the height of "Play all"; its tooltip names the mode it switches to.
- Track cards: the toggle's card mode shows the selected playlist's tracks in `VirtualizingAdaptiveGrid` (`TrackCardItem` style): cover at the source ratio, title, then artist with the time at its right, always visible. The playing card is solid accent with white text; double-click plays from it; the column header row is hidden. The mode is a session-wide static like the column options, not saved.
- Cards: `res:AdaptiveGrid` (MinItemWidth 140, MaxItemWidth 320, Spacing 12): cards share the full width and a column is added once every card still gets 140. Cover height follows width through `MultiplyConverter` and a per-source ratio (YouTube 16:9, others square). A card's border is `AppStrokeBrush`; accent only for "now playing". Keyboard focus shows the dotted focus visual, never a blue border.
- List: own `ListViewItem` template (Border, CornerRadius 4, Margin `0,1`, Padding `16,10,12,10`), triggers in the order hover (`AppHoverBrush`), selected (`AppSelectedBrush`), playing (`AppAccentBrush` with `AppAccentTextBrush` text), playing plus hover (`AppAccentHoverBrush`).
- Columns: a header row (`Subtle`, FontSize 12, margin `17,0,13,4` to line up with the rows) whose widths bind TwoWay to star `GridLength` properties on the view model; rows bind OneWay. Name and time always visible; optional columns (#, artist) toggle from a right-click `ContextMenu` on header and list, # hidden by default. Hidden columns get width 0 and collapsed content. A 1 px hairline runs between Title and Artist through header and every row.
- Text cells: `TextTrimming="CharacterEllipsis"` plus `res:Interaction.FullTextToolTip="True"`, so hover shows the full value only when it is cut off. No generic hint tooltips on rows.
- Dividers: `HairlineSplitter` everywhere (1 px `AppStrokeBrush`, 9 px hit area, accent on hover and drag).
- Scrollbars and tooltips: the app-wide implicit styles (4 px blue thumb of constant thickness in a 10 px hit area, faint rail and darker accent on direct hover; card tooltip with 8 px corners, border, soft shadow, wrapping at 420).
- Interaction: hand cursor on clickable rows and cards, double-click a row to play from it, right-click a card for its own actions (Settings..., Remove on added playlists).
- Shared list styles: the row style is `TrackListItem` in `Styles.xaml` (each view adds only its own `res:Interaction.DoubleClickCommand` setter), with `TrackTitle`, `TrackSubtle`, `TrackDivider` and `TrackHeader` for the cells and the header row. Used by YouTube, My Music and Home Share.
- Wide cards: Home's speaker cards use `res:AdaptiveGrid` with MinItemWidth 340 and a MaxItemWidth so large that the row always fills; a single speaker's card spans the full width.
- Section actions: an action that belongs to one section is an icon at the right end of the section heading, and the heading keeps the height of every other heading (App settings: Add folder as the `+` glyph). `AccentIconButton` (an `IconButton` in `AppAccentBrush`) is used only for the Music folders add and trash icons; apart from the accent-filled list/card toggle (see Buttons), every other icon button stays neutral.

## State

- Blue is the action and "now playing" colour: the playing row is solid accent, the playlist it plays from gets a 1 px accent border. Inside the content area, rows and cards never turn blue for focus or selection (grey `AppSelectedBrush`, dotted focus visual); the sidebar's accent marker for the current page stays.
- Data appears from cache first and refreshes in the background; a page connects its source on load, so its state never shows "Not connected" while it works.

## Pages with a different structure (group C)

These pages take the principles and the shared building blocks, never the two-pane layout.

- Settings pages (owner: "consider using 2 cols (responsive)", then "go"): title only; settings in two columns that become one below 784 DIP of content (columns of at least 380, Spacing 24). Device settings uses `res:AdaptiveGrid` (`SettingsGrid`) because every cell is one line; App settings uses the masonry panel `res:ColumnFlow` (`SettingsColumns`) because its sections differ in height and `AdaptiveGrid` would stretch each row to the tallest. Label above the input (`FieldLabel`), a hairline under each cell (`SettingCell`) or under each section heading (`SectionHeading` plus `SectionRule`), inputs full width with Apply, Run or Switch at the end of the row. App settings has one Save, at the top right outside the scroller, on the content's right edge. Tabs on Device settings stay.
- Now playing (owner: "remove the duplicate controls, go"): `PageTitle` "Now playing", a square cover in a `Viewbox` that scales with the window (columns `1.1*` and `*`, 28 gap), text centred beside it: title at most three lines then an ellipsis (`NowPlayingTitle`), artist at most two (`NowPlayingArtist`), album one line (`NowPlayingAlbum`), quality badge and speaker on one quiet line. No buttons: the player bar is the only control surface. `Interaction.FullTextToolTip` detects a wrapped, height-clamped title by height.

## Corrections that produced this (do not repeat)

| Rejected | Accepted |
| --- | --- |
| Fixed-width URL box with a label in front, connect buttons in a separate right column | Full-width box with the hint inside, the action at its end |
| Status, cookie and connection hint lines under the title | Title only; state in the sidebar |
| One primary button per page, the rest plain (design-skill default) | Every text button blue with white text, equal min width |
| Fixed 160 px cards in a `WrapPanel` leaving empty space | Cards sharing the width with an adaptive column count |
| Square YouTube covers making cards tall and the pane scroll | 16:9 covers for YouTube |
| Light blue tint for the playing row | Solid accent row with white text, darker on hover |
| Fluent's hover painting light grey over white text | Own `ListViewItem` template |
| 5 px grey splitter bars | 1 px hairlines with a wide hit area |
| "Double-click to play" tooltip on every row | Full-value tooltip only on trimmed cells |
| Fluent's expanding grey scrollbar | Thin blue scrollbar, same thickness, subtle hover |
| Blue border on the focused card | Blue border only on the playing playlist's card |
| Fixed-width search and input boxes (My Music 320, Radio 360, Home 180, Home Share's server box 280 with a "Server" label) | Full width, hint inside, the action at the end |
| Fixed 340 px speaker cards in a `WrapPanel` | Cards filling the row through `AdaptiveGrid` |
| Right gap wider than the left (scrollbar column plus the content's right margin) | Equal 28 DIP margins, scrollbar inside the right margin ("right margins are the problem") |
| Prev, play, next and queue buttons on Now playing repeating the player bar ("do we need double control chrome?") | The player bar as the only control surface |
| Add folder as a blue text button in the heading, then under the list, stacked below Save ("buttons are not nice") | A blue `+` icon at the right end of the Music folders heading, blue trash icons |
| Save sticking out 10 DIP right of the content below it | Save and section actions on the content's right edge |
| App settings capped at 760 px, a label column, fixed-width boxes, a second Save at the bottom | Two responsive columns, label above, full-width inputs, one Save top right |
| The list/card toggle as a neutral `IconButton` ("this should be a blue button (action)") | Accent fill, white glyph, the height of "Play all" |
| Track cards without the time ("to the cards add time information for the track") | Time at the right of the artist line on every card |

## Open

- The sidebar service switches (`SwitchButton`) use `AppSuccessBrush` green, which predates the "blue means action" rule; the owner has not decided whether they turn blue.
- Implemented 2026-10-19 without an explicit approval yet: My Music (album and genre cards in `AdaptiveGrid` with square covers, both track lists with #, Title, Artist, Album, Time columns toggled by right-click, scan status beside the scan buttons, "Play all" at the right of the drill-down header) and Home Share (the current folder as the list title with a blue "Play all" at its right, a Name and Time header). Their rows have no now-playing state.
- Home Share and Queue: the rightmost item is an `IconButton` whose glyph sits about 10 DIP inside its 36 DIP box, so the visible right gap reads 57 px against 42 on the left. Moving those icons out so the glyph meets the margin was offered; the owner has not answered.
