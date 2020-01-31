// Note: In order to run this code from nodejs scripts without
// having to use babel-node, this code uses `require` instead of
// `import`, `exports` instead of `export`, etc.

const fs = require('fs');//.promise;
const path = require('path');

exports.listFiles = async function(root) {
    async function _ (root){
        // TODO: make sure root exists and is a dir, or just
        //    let fs.readdir throw exception
        console.log("lising " + root)

        if (!root || typeof(root) !== 'string') {
            throw "Invalid root dir: " + root;
        }

        let fileList = {files: [], dirs: []};

        // TODO get this to work with  `await require('fs').promise.readdir(...)`
        (fs.readdirSync(root, {withFileTypes:true})).map(async (dirent) => {
            if (dirent.isDirectory()) {
                let dirFileList = null;
                try {
                    dirFileList = await _(path.join(root, dirent.name));
                } catch(err) {
                    console.log("ERROR: " + err)
                    dirFileList = {files: [], dirs: [], error: err};
                }
                dirFileList.name = dirent.name
                fileList.dirs.push(dirFileList)

            } else if (dirent.isFile()) {
                fileList.files.push(dirent.name)
            }
        })
        return fileList;
    }
    return await _(root);
}
