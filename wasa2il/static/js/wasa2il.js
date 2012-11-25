

function document_propose(doc, val) {
	$.getJSON("/api/propose/", {"document": doc, "status": val}, function(data) {
		if (data) {
			
		}
	});
}


