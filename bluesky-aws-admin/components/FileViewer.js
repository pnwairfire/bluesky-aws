import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'

import LoadingSpinner from './LoadingSpinner';
import { ApiClient } from '../lib/apiutils'
import styles from './RunLog.module.css'



// TODO: handle case where query param 'name' either isn't specified
//   or points to a non-existing file.  In this situation, you get
//   a blank page




export default function RunLog(props) {
    if (props && props.request && props.run) {

        let path ='/api/requests/' + encodeURIComponent(props.request)
            + '/runs/' + encodeURIComponent(props.run) + '/output-files/file'
        let query = { name: encodeURIComponent(props.name)}
        let {data, fetchError} = ApiClient.get(path, query);
        let contents = data && data.file && data.file.contents;
        let error = fetchError || (data && data.error);



        // TODO: use ReactJson instead of textarea for json data files
        // import dynamic from 'next/dynamic';
        // const ReactJson=dynamic(import ('react-json-view'),{ssr:false});


        // TODO: download & copy to clipboard
        //   - implement download button, generating download from api
        //     response, not a direct download from server
        //   - implement copy to clipboard
        //   - use glyicon for download & copy to clipboard buttons
        //   - stylbe buttons - padding, etc.

        return (
            <div>
                <h5>Run Log</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {contents &&
                    <div>
                        <div>
                            <Button variant="outline-dark" size="sm"
                                onClick={()=>{alert("Not Implemented")}}>Download</Button>
                            <Button variant="outline-dark" size="sm"
                                onClick={()=>{alert("Not Implemented")}}>Copy to Clipboard</Button>
                        </div>
                        <textarea className={styles.logtext} value={contents} disabled />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};