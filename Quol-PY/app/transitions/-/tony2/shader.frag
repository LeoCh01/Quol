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
    float full_time = u_time * 2.0f;

    if(l < full_time) {
        if(l > full_time - 0.1f)
            gl_FragColor = texture(u_tex, texUV + noise(texUV * 5.0f + u_seed) + u_time);
        else
            gl_FragColor = vec4(0.0f);
    }
    else
        gl_FragColor = texture(u_tex, texUV);
}