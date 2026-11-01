// Run: node --experimental-vm-modules smoke_test.mjs
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(fileURLToPath(import.meta.url))
const read = name => fs.readFileSync(path.join(root, name), 'utf8')
const routes = JSON.parse(read('pages.json'))
const registered = new Set(routes.pages.map(page => page.path))
const tabs = new Set(routes.tabBar.list.map(page => page.pagePath))
let scripts = 0
let links = 0
for (const page of routes.pages) {
	const source = read(page.path + '.vue')
	const script = source.match(/<script[^>]*>([\s\S]*?)<\/script>/)?.[1]
	if (script) {
		new vm.SourceTextModule(script)
		scripts++
	}
	for (const match of source.matchAll(/['"`]\/((?:pages\/)[\w/]+)(?:[?'"`])/g)) {
		assert(registered.has(match[1]), 'Unregistered link: ' + match[1])
		links++
	}
	assert(!/https?:\/\/(?:localhost|127\.0\.0\.1)/.test(source))
}
assert(!registered.has('pages/index/index'))
assert(!fs.existsSync(path.join(root, 'pages/index/index.vue')))
for (const tab of tabs) assert(registered.has(tab))

async function configFor(origin) {
	const module = new vm.SourceTextModule(read('utils/config.js'), {
		initializeImportMeta(meta) { meta.env = { VITE_API_ORIGIN: origin } }
	})
	await module.link(() => {})
	await module.evaluate()
	return module.namespace
}
const remote = await configFor(' https://api.example.com/// ')
assert.equal(remote.BASE_URL, 'https://api.example.com/api/v1')
assert.equal(remote.resolveMediaUrl('/api/v1/uploads/avatar.png'), 'https://api.example.com/api/v1/uploads/avatar.png')
assert.equal(remote.resolveMediaUrl('https://cdn.example.com/a.png'), 'https://cdn.example.com/a.png')
assert.equal(remote.resolveMediaUrl(null), '')
assert.equal((await configFor('')).BASE_URL, '/api/v1')

let stack = [{}]
const calls = []
const context = vm.createContext({
	getCurrentPages: () => stack,
	uni: {
		switchTab: options => calls.push(['tab', options.url]),
		reLaunch: options => calls.push(['launch', options.url]),
		navigateBack: options => { calls.push(['back', options.delta]); if (stack[0].fail) options.fail() }
	}
})
const nav = new vm.SourceTextModule(read('utils/navigation.js'), { context })
await nav.link(() => {})
await nav.evaluate()
nav.namespace.navigateBack('/pages/teach/TeachHome')
assert.deepEqual(calls.pop(), ['tab', '/pages/teach/TeachHome'])
nav.namespace.navigateBack('/pages/auth/Login', false)
assert.deepEqual(calls.pop(), ['launch', '/pages/auth/Login'])
stack = [{}, {}]
nav.namespace.navigateBack()
assert.deepEqual(calls.pop(), ['back', 1])
stack[0].fail = true
nav.namespace.navigateBack('/pages/profile/Profile')
assert.deepEqual(calls.pop(), ['tab', '/pages/profile/Profile'])
assert.deepEqual(calls.pop(), ['back', 1])
console.log(`PASS: ${scripts} page scripts parsed; ${links} registered links checked; configurable API/media URLs and four back-navigation scenarios.`)
