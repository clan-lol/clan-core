/**
 * use this template literal to write tailwind classes
 * example: tw`transition-colors duration-300 ease-in-out active:duration-100`
 *
 * to use this, you need to add the following to your tailwind plugin configuration (Intellij settings)
 *   "experimental": {
 *     "classRegex": ["tw`(.*)`"]
 *   }
 */
export const tw = String.raw;
