import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../lib/status'

export default async (req, res) => {
    const {
        query: { request },
    } = req

    res.statusCode = 200
    res.setHeader('Content-Type', 'application/json')
    res.end(JSON.stringify({
        request: req.query.request,
        status: await getRequestStatus(
            process.env.s3.bucketName, req.query.request)
    }))
}
