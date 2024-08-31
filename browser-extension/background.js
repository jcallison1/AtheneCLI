chrome.runtime.onMessage.addListener(
	(request, sender, sendResponse) => {
		if (request?.message === "get_athene_token" && sender.tab) {
			chrome.cookies.get({
				name: "PHPSESSID",
				url: "https://athenecurricula.org/",
				storeId: sender.tab.cookieStoreId,
			})
			.then((cookie) => {
				sendResponse(cookie?.value);
			});
			
			// Return true so that sendResponse stays valid after the callback ends
			return true;
		}
		
		return false;
	}
);
