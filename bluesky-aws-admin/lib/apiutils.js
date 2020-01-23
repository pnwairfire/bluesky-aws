import fetch from 'unfetch'
import useSWR from 'swr'

export async function fetcher(url) {
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

    static formUrl(path, query) {
        path = path.replace(/^\/+/, '').replace(/\/+$/, '');
        query = Object.keys(query || {}).map(key => key + '=' + query[key]).join('&');
        return ENDPOINT_BASE + '/' + path + '?' + query;
    }

    static get(path, query) {
        let url = this.formUrl(path, query)
        return useSWR(url, fetcher);
    }

    static getNoSwr(path, query) {
        let url = this.formUrl(path, query)
        return fetcher(url);
    }
}

export class ApiServerUtils {
    static writeReponse(res, body) {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(body));
    }
}
