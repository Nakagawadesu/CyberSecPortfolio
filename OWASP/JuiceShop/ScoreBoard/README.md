# OWASP Juice Shop: Score Board Challenge 🎯

### 🕵️‍♂️ Methodology

To solve the "Find the Score Board" challenge, I performed static analysis on the application's minified JavaScript bundle.

🔍 The Finding

After formatting the code, I analyzed the SideNav component (selectors: [['sidenav']]) and discovered the routing configuration in the consts array:
```bash
[
  'mat-list-item',
  '',
  'routerLink',
  '/score-board', // <--- HIDDEN ROUTE FOUND
  'aria-label',
  'Open score-board'
]
```

### ✅ Solution

The Score Board is accessible at:
```bash
/#/score-board
```