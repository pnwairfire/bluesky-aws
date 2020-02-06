import { Component } from 'react';

import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import LoadingSpinner from './LoadingSpinner';
import { ApiClient } from '../lib/apiutils'
import styles from './FileViewer.module.css'



// TODO: handle case where query param 'name' either isn't specified
//   or points to a non-existing file.  In this situation, you get
//   a blank page




export default function FileViewer(props) {
    if (props && props.request && props.run) {

        let path ='/api/requests/' + encodeURIComponent(props.request)
            + '/runs/' + encodeURIComponent(props.run) + '/output-files/file'
        let query = { name: encodeURIComponent(props.name)}
        console.log('Querying file to view: ' + path + '?name='+query.name);
        let {data, fetchError} = ApiClient.get(path, query);
        let contents = data && data.file && data.file.contents;
        let error = fetchError || (data && data.error);


        // TODO: download & copy to clipboard
        //   - implement download button, generating download from api
        //     response, not a direct download from server
        //   - implement copy to clipboard
        //   - use glyicon for download & copy to clipboard buttons
        //   - stylbe buttons - padding, etc.

        return (
            <div className={styles['file-viewer']}>
                <h5>{props.name}</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {contents &&
                    <div className={styles['content-wrapper']}>
                        <div className={styles['buttons-wrapper']}>
                            <DownloadButton contents={contents} filename={props.name} />
                            <Button variant="outline-dark" size="sm"
                                onClick={()=>{alert("Not Implemented")}}>Copy to Clipboard</Button>
                        </div>
                        <ContentsWrapper contents={contents} name={props.name} />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};

const EXT_SKIP_MATCHER = /\.(nc|con|kmz|png)$/

function ContentsWrapper(props) {
    if (props.name.endsWith('.json')) {
        try {
            let jsonData = JSON.parse(props.contents)
            return (
                <div className={styles['json-viewer']}>
                    <ReactJson src={jsonData} theme="monokai" />
                </div>
            )
        } catch(err) {
            // fall back to using textarea, below
            console.log("Failed to parse and display json contents of " + props.name)
        }
    }

    // TODO: getting rendering of in-memory image data working.
    //   Current issues:
    //    - image data in props.contents seems to be corrupted
    //    - need to implement conversion to base 64
    //   Otherwise, When I hard code base64 image data, the following
    //   code does work
    //   If we get this working, remove 'png' from EXT_SKIP_MATCHER
    // else if (props.name.endsWith('.png')) {
    //     // TODO: convert props.contents to base64 string
    //     let base64img = ''
    //     let data = 'data:image/png;base64,' + base64img;
    //     return (
    //         <img src={data} />
    //     )
    // }

    else if (EXT_SKIP_MATCHER.test(props.name)) {
        return (
            <div>(No Preview)</div>
        )
    }

     // default (and fallback, in case json contents fail to parse) is to
     // display contents in tedtarea
    return (
        <textarea value={props.contents} disabled />
    )
}

class DownloadButton extends Component {

    constructor(props) {
        super(props);

        this.state = {};
    }


    handleClick = data => {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,'
            + encodeURIComponent(this.props.contents));
        element.setAttribute('download', this.props.filename);
        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    }

    render() {
        return (
            <Button variant="outline-dark" size="sm"
                onClick={this.handleClick}>Download</Button>
        )
    }
}