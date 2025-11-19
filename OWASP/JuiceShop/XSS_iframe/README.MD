# 💉 OWASP Juice Shop: DOM XSS Challenge

## 🎯 Challenge Goal

Perform a DOM-based Cross-Site Scripting (XSS) attack using the search bar to execute a malicious script in the victim's browser.

🧪 Payload Testing

### 1. HTML Injection (Proof of Concept)

Payload:
```javascript
<h1>owasp
```

Result: ✅ Success
Observation: The application reflected the HTML tag, rendering the text "owasp" as a large header. This confirms the input is not being properly encoded before being rendered in the DOM.

### 2. Standard Script Injection

Payload:
```javascript
<script>alert('xss')</script>
```

Result: ❌ Failed
Analysis: While the tag might be inserted into the DOM, modern browsers do not execute <script> tags inserted via innerHTML dynamically. This is a browser-level security specification, not necessarily a filter by the app.

### 3. Iframe Injection (The Solution)

Payload:
```javascript
<iframe src="javascript:alert(`xss`)">
```

Result: ✅ Success (Alert popped up)

🕵️‍♂️ Technical Analysis: Why <script> failed but <iframe> worked

The application (Angular) likely uses a method similar to bypassSecurityTrustHtml for the search results, allowing raw HTML to be rendered. However, we still faced a browser constraint.

The Browser Restriction:
When HTML is added to the DOM dynamically (e.g., using element.innerHTML = '...'), the HTML5 specification dictates that any <script> tags found within that string must not be executed. This prevents simple reflected XSS even if the application is vulnerable.

The Bypass (iframe):
The <iframe> tag creates a new nested browsing context. It is not subject to the same "dead code" restriction as the <script> tag when inserted dynamically.

The Vector (Pseudo-Protocol):
By setting the src attribute to javascript:..., we are using a pseudo-protocol.

Instead of fetching a URL (like http://...), the browser interprets the content as executable JavaScript code.

The return value of this code becomes the content of the frame.

The execution happens immediately upon the frame loading, successfully triggering the alert().

### 🔗 Vulnerable URL (PoC)

You can reproduce the exploit by navigating directly to:

http://localhost:3000/#/search?q=%3Ciframe%20src%3D%22javascript%3Aalert(%60xss%60)%22%3E
