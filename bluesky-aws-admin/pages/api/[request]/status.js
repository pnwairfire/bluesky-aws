import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../lib/status'

export default (req, res) => {
    const {
        query: { request },
    } = req

    res.statusCode = 200
    res.setHeader('Content-Type', 'application/json')
    res.end(JSON.stringify({
        request: req.query.request,
        status: getRequestStatus(req.query.request)
    }))
}
