async function getWithAuthAlert(url) {
    var response = await fetch(url);
    if (response.status === 401 || response.status === 403) {
        alert("You are not logged in or in the correct group.");
    } else {
        return response;
    }
}

function init() {
    return {
        servers: [],
        currentServers: [],
        oldServers: [],
        serverStatus: [],
        charts: [],
       
        minutesAgo(dateStr) {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            return diffMins + ' min ago';
        },

        getStatus(serverId) {
            // format is {_id: serverId, count: count}
            const status = this.serverStatus.find(s => s._id === serverId);
            if (status) {
                return status.count;
            } else {
                return 0;
            }
        },

        async loadList() {
            console.log('Loading List');
            var result = await (await getWithAuthAlert('/api/crud/servers')).json();
            var statusResult = await (await getWithAuthAlert('/api/analytics/serverStats')).json();
            this.serverStatus = statusResult;
            console.log(this.serverStatus);
            //console.log(result);
            this.servers= result;
            // if the servrs have been seen in last 2 hours, it is current, otherwise it is old
            this.currentServers = this.servers.filter(s => { 
                const lastSeen = new Date(s.lastSeen.$date);
                const now = new Date();
                const diffMs = now - lastSeen;
                const diffHours = diffMs / (1000 * 60 * 60);
                return diffHours <= 2;
            });
            this.oldServers = this.servers.filter(s => { 
                const lastSeen = new Date(s.lastSeen.$date);
                const now = new Date();
                const diffMs = now - lastSeen;
                const diffHours = diffMs / (1000 * 60 * 60);
                return diffHours > 2;
            });
            var chartsResult = await (await getWithAuthAlert('/api/crud/getPageConfig/servers')).json();
            this.charts = chartsResult.charts;
        }, 

        async updateServer(server) {
            console.log('Updating server', server);
            await fetch('/api/crud/updateServer', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({name: server._id, nextPoll: parseInt(server.nextPoll)})
            });
            alert('Server updated successfully');
        }

    }
}