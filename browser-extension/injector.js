function addCopyLink(linkText, copyText) {
	const elem = document.createElement("a");
	
	elem.appendChild(document.createTextNode(linkText));
	elem.href = "javascript:;";
	
	elem.addEventListener("click", () => {
		navigator.clipboard.writeText(copyText);
	});
	
	document.body.appendChild(elem);
	document.body.appendChild(document.createElement("br"));
}

const url = new URL(window.location.href);
const urlMatch = url.pathname.match(new RegExp("^/problem/(\\w+)/?$"));

if (urlMatch !== null) {
	const assignmentId = urlMatch[1];
	
	document.body.appendChild(document.createElement("br"));
	
	addCopyLink("Click to copy assignment id", assignmentId);

	(async () => {
		// HTTP-Only cookies can only be accessed using the browser's cookies API,
		//  and the cookies API can only be used in a background script. So I have to
		//  send a message to the background script to have it fetch the cookie.
		const response = await chrome.runtime.sendMessage({ message: "get_athene_token" });
		
		if (response !== undefined) {
			addCopyLink("Click to copy auth token", response);
		}
	})();
}
