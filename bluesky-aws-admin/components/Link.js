// Copied and modified from:
// https://levelup.gitconnected.com/deploy-your-nextjs-application-on-a-different-base-path-i-e-not-root-1c4d210cce8a

import NextLink, { LinkProps } from 'next/link'
import { format } from 'url'
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

// TODO: make sure intelligently join
//   publicRuntimeConfig.basePath and props.href/as

export default ({ children, ...props }) => {
    console.log('basePath:  ' + publicRuntimeConfig.basePath);
    console.log('href: ' +  props.href)
    console.log('as: ' +  props.as)

    if (process.env.links.useNextLink) {
        // The following results in the error
        //  "Mismatching `as` and `href` failed to manually
        //   provide the params: request in the `href`'s `query`"
        // when basePath (in next.config.js) it set to nonemtpy string
        // TODO: figure out how to get this working and switch to always
        //    using next/link Link's
        return (
          <NextLink
            {...props}
            as={`${publicRuntimeConfig.basePath || ''}${format(props.as)}`}
          >
            {children}
          </NextLink>
        )
    } else {
        return (
            <a href={`${publicRuntimeConfig.basePath || ''}${format(props.as)}`}>
                {children.props.children}
            </a>
        )
    }
}
