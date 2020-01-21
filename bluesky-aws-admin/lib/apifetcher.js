import fetch from 'unfetch'
import useSWR from 'swr'

const API_URL = "http://localhost:3000"; //window.location.href;
async function fetcher(path) {
    const res = await fetch(API_URL + path)
    const json = await res.json()
    return json
}

export default function fetchapi (path) {
    return useSWR(path, fetcher);
}
