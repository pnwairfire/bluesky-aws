import fetch from 'unfetch'
import useSWR from 'swr'

async function fetcher(url) {
    const res = await fetch(url)
    const json = await res.json()
    return json
}

// TODO: dynamically determine endpoint
const ENDPOINT_BASE = 'http://localhost:3000';

export class ApiClient {
    // constructor(endpointBase) {
    //   this.endpointBase = endpointBase.replace(/\/+$/, '');
    // }

    static get(path, query) {
        path = path.replace(/^\/+/, '');
        query = Object.keys(query || {}).map(key => key + '=' + query[key]).join('&');
        let url = ENDPOINT_BASE + '/' + path + '?' + query;
        return useSWR(url, fetcher);
    }
}

export class ApiServerUtils {
    static writeReponse(res, body) {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(body));
    }
}
