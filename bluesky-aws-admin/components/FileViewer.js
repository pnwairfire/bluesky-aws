import { Component } from 'react';
import path from 'path';
import Router from 'next/router'
import { FaExpandArrowsAlt, FaFileDownload } from "react-icons/fa";
import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'
import OverlayTrigger from 'react-bootstrap/OverlayTrigger'
import Tooltip from 'react-bootstrap/Tooltip'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import LoadingSpinner from './LoadingSpinner';
import { ApiClient } from '../lib/apiutils'
import styles from './FileViewer.module.css'
import Link from './Link';



// TODO: handle case where query param 'name' either isn't specified
//   or points to a non-existing file.  In this situation, you get
//   a blank page




export default function FileViewer(props) {
    if (props && props.apiPath) {

        console.log('Querying file to view: ' + props.apiPath +
             ' ' + props.fileName);
        let {data, fetchError} = ApiClient.get(props.apiPath,
            {name: encodeURIComponent(props.fileName)});
        let contents = data && data.file && data.file.contents;
        let fileName = (data && data.file && data.file.name) || props.fileName;
        let error = fetchError || (data && data.error);


        // TODO: download & copy to clipboard
        //   - implement download button, generating download from api
        //     response, not a direct download from server
        //   - implement copy to clipboard
        //   - use glyicon for download & copy to clipboard buttons
        //   - stylbe buttons - padding, etc.

        return (
            <div className={styles['file-viewer']}>
                <h5>{props.header || fileName}</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {contents &&
                    <div className={styles['content-wrapper']}>
                        <div className={styles['buttons-wrapper']}>
                            <DownloadButton contents={contents} filename={fileName} />
                            {props.fullPageLink &&
                                <ViewInFullPageButton fullPageLink={props.fullPageLink} />
                            }
                        </div>
                        <ContentsWrapper contents={contents} fileName={fileName} />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};


const EXT_SKIP_MATCHER = /\.(nc|con|kmz)$/

function ContentsWrapper(props) {
    if (props.fileName.endsWith('.json')) {
        try {
            let jsonData = (typeof props.contents === 'string'
                    || props.contents instanceof String) ?
                JSON.parse(atob(props.contents)) : props.contents;

            return (
                <div className={styles['json-viewer']}>
                    <ReactJson src={jsonData} theme="monokai" />
                </div>
            )
        } catch(err) {
            // fall back to using textarea, below
            console.log("Failed to parse and display json contents of "
                + props.fileName + ": " + err)
        }
    }

    else if (props.fileName.endsWith('.png')) {
        let data = 'data:image/png;base64,' + props.contents;
        return (
            <div className={styles['image-viewer']}>
                <img src={data} />
            </div>
        )
    }

    else if (EXT_SKIP_MATCHER.test(props.fileName)) {
        return (
            <div>(No Preview)</div>
        )
    }

     // default (and fallback, in case json contents fail to parse) is to
     // display contents in tedtarea
    return (
        <textarea value={atob(props.contents)} disabled />
    )
}


class DownloadButton extends Component {

    constructor(props) {
        super(props);

        this.state = {};
    }

    handleClick = data => {
        saveByteArray(this.props.contents, this.props.filename)
    }

    render() {
        return (
            <OverlayTrigger key="download"
                placement="top"
                delay={{ show: 250, hide: 250 }}
                overlay={
                    <Tooltip id="tooltip-download">
                        Download
                    </Tooltip>
                }
            >
                <Button variant="outline-dark" size="sm"
                    onClick={this.handleClick}>
                    <FaFileDownload />
                </Button>
            </OverlayTrigger>
        )
    }
}

// base64ToArrayBuffer and saveByteArray were copied from
// http://jsfiddle.net/VB59f/2  and modified appropriately

function base64ToArrayBuffer(base64) {
    var binaryString = atob(base64);
    var binaryLen = binaryString.length;
    var bytes = new Uint8Array(binaryLen);
    for (var i = 0; i < binaryLen; i++)        {
        var ascii = binaryString.charCodeAt(i);
        bytes[i] = ascii;
    }
    return bytes;
}

function saveByteArray(data, name) {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    let buffer = [base64ToArrayBuffer(data)];
    let blob = new Blob(buffer, {type: "octet/stream"});
    let url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = path.basename(name);
    a.click();
    document.body.removeChild(a);
}


class ViewInFullPageButton extends Component {

    constructor(props) {
        super(props);
        this.state = {};
    }

    handleClick = data => {
        Router.push(this.props.fullPageLink.asPath)
    }

    render() {
        return (
            <Link href={this.props.fullPageLink.hrefPath}
                    as={this.props.fullPageLink.asPath}>
                <OverlayTrigger key="viewinfullpage"
                    placement="top"
                    delay={{ show: 250, hide: 250 }}
                    overlay={
                        <Tooltip id="tooltip-viewinfullpage">
                            View Full Page
                        </Tooltip>
                    }
                >
                    <Button variant="outline-dark" size="sm"
                            onClick={this.handleClick}>
                        <FaExpandArrowsAlt />
                    </Button>
                </OverlayTrigger>
            </Link>
        )
    }
}
