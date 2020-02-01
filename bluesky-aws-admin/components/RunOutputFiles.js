import path from 'path'
import Alert from 'react-bootstrap/Alert'

import Link from './Link';
import { ApiClient } from '../lib/apiutils'
import LoadingSpinner from './LoadingSpinner';
import styles from './RunOutputFiles.module.css'

export default function RunOutputFiles(props) {

    if (props && props.request && props.run) {
        let path ='/api/requests/' + encodeURIComponent(props.request)
            + '/runs/' + encodeURIComponent(props.run) + '/output-files'
        let {data, fetchError} = ApiClient.get(path);

        let outputFiles = data && data.outputFiles;
        let error = fetchError || (data && data.error);

        return (
            <div className={styles['run-output-files']}>
                <h5>Run Output Files</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {outputFiles &&
                    <div className={styles['run-output-files-list']}>
                        <DirContents
                            request={props.request}
                            run={props.run}
                            files={outputFiles.files}
                            dirs={outputFiles.dirs}
                            name={outputFiles.name} />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};

function DirContents(props) {
    if (props.files || props.dirs) {
        return (
            <div className={styles['dir']}>
                <div>{(props.name) ? (props.name + '/') : ('')}</div>
                <div className={styles['contents']}>
                    {props.files && props.files.map((filename) =>{
                        let query = {name: encodeURIComponent(path.join(props.dirPath||'', filename))};
                        let hrefPath = "/requests/[request]/runs/[run]/output-files/view";
                        let asPath = `/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.run)}/output-files/view`
                        return (
                            <div>
                                <Link href={{ pathname: hrefPath, query: query }}
                                        as={{ pathname: asPath, query: query}}>
                                    <a>{filename}</a>
                                </Link>
                            </div>
                        )
                    })}
                    {props.dirs && props.dirs.map((data) =>{
                        return (
                            <DirContents files={data.files}
                                dirs={data.dirs} name={data.name} />
                        )
                    })}
                </div>
            </div>
        )
    } else {
        return null
    }
}
