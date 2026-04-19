#version 330 core

in vec2 texUV;

uniform float u_time;
uniform vec2 u_res;
uniform sampler2D u_tex;
uniform float u_seed;

float rand(vec2 p)
{
	vec3 p2 = vec3(p.xy,1.0);
    return fract(sin(dot(p2,vec3(37.1,61.7, 12.4)))*3758.5453123);
}

float noise(vec2 n) {
	const vec2 d = vec2(0.0, 1.0);
  vec2 b = floor(n), f = smoothstep(vec2(0.0), vec2(1.0), fract(n));
	return mix(mix(rand(b), rand(b + d.yx), f.x), mix(rand(b + d.xy), rand(b + d.yy), f.x), f.y);
}


void main()
{
    float l = length(texUV - 0.5f);
    float t = u_time * 2.0f;

    for(int i = 0; i < 4; i++) {
        float n = t - i * 0.4;

        if(n < 0.0f)
            break;

        if(n < l && n > l - 0.1f) {
            gl_FragColor = vec4(texture(u_tex, texUV + noise(texUV * 5.0f + u_seed) / 10.0f).rgb, 1.0f - u_time);
            return;
        }
    }

    gl_FragColor = vec4(texture(u_tex, texUV).rgb, 1.0f - u_time - 0.1f);
}