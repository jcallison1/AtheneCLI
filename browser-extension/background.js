chrome.runtime.onMessage.addListener(
	(request, sender, sendResponse) => {
		if (request?.message === "get_athene_token") {
			chrome.cookies.get({
				name: "PHPSESSID",
				url: "https://athenecurricula.org/"
			})
			.then((cookie) => {
				sendResponse(cookie?.value);
			});
			
			// Return true so that sendResponse stays valid after the callback ends
			return true;
		}
	}
);
