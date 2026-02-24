async function getWithAuthAlert(url) {
    var response = await fetch(url);
    if (response.status === 401 || response.status === 403) {
        alert("You are not logged in or in the correct group.");
    } else {
        return response;
    }
}