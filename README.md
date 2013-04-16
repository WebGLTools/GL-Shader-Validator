# GL Shader Validator

![image](http://aerotwist.com/glshadervalidator/screenshot.png)

This is a [Sublime Text 2 / 3](http://www.sublimetext.com/) plugin that passes GLSL / ESSL to ANGLE's
preprocessor / compiler for validation.
Any errors that ANGLE finds are routed back to Sublime and the tokens in
the shader are highlighted for your convenience and debugging joy.
To see the details of the error check the status message in the bottom left of the
Sublime view.

## Installation

**You can, and probably should, install GL Shader Validator via [Package Control](http://wbond.net/sublime_packages/package_control)**

If you would like to install it manually, clone this repo into your packages folder
(typically ~/Library/Application Support/Sublime Text 2/Packages).

```
cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages
git clone git://github.com/WebGLTools/GL-Shader-Validator.git "GL Shader Validator"
```

If you're on Windows 7 the path looks more like this, assuming you have Git installed:

```
cd c:\users\YOUR_ACCOUNT\AppData\Roaming\Sublime Text 2\Packages
git clone git://github.com/WebGLTools/GL-Shader-Validator.git "GL Shader Validator"
```

Also if you're using Sublime Text 3 then you just switch the `2` in the path above to `3` and you should be all set.

## Usage

Assuming that you have a [GLSL / ESSL syntax highlighter](https://github.com/euler0/sublime-glsl) installed in Sublime, all you should need to do
is install the plugin and your shader code will be validated as expected.

It's worth saying that ANGLE expects vertex shaders to have the file
suffix `.vert` and fragment shaders `.frag`. If you do not name your files
with that suffix ANGLE (and therefore the plugin) will not be able
to validate your shaders. Sadness will ensue.

You can set the default specification to use in the settings:
```
Preferences > Package Settings > GL Shader Validator > Settings - Default
```

This can be overridden in a specific shader by adding comments:
`/* spec: webgl */` for WebGL,
`/* spec: es2 */` for OpenGL ES 2.0 or
`/* spec: css */ ` for Custom Filters / CSS Shaders

## Permissions

This plugin requires use of a command line utility called essl_to_glsl, which is bundled with the plugin. By default,
however, the utility will not have execute permissions. The plugin will attempt to enable those permissions automatically when it loads, but
should that fail you will receive the following error message:

> GLShaderValidator: permission denied to use essl_to_glsl command

In such instances you should enable execute permissions yourself:

```
cd ~/Library/Application Support/Sublime Text 2/Packages/GL\ Shader\ Validator
chmod +x essl_to_glsl
```

## Settings

You can modify the settings file (`GLShaderValidator.sublime-settings`) inside
the plugin folder. You will find the documentation for the settings in
that file. There aren't many of those right now, but if you want more let us
know via the repo's Issues.

## Credits

* [Paul Lewis](http://aerotwist.com)
* [Brendan Kenny](http://extremelysatisfactorytotalitarianism.com/)
