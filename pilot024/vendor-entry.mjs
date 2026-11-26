import * as Channel from 'jschannel';
export const build=Channel.build||Channel.default?.build;
if(typeof build!=='function')throw new Error('JSChannel build unavailable');
