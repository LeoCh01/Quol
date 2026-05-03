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

float noise(in vec2 p)
{
    vec2 i = floor(p);
	vec2 f = fract(p);
	f *= f * (3.0-2.0*f);

    return mix(mix(rand(i + vec2(0.,0.)), rand(i + vec2(1.,0.)),f.x),
		mix(rand(i + vec2(0.,1.)), rand(i + vec2(1.,1.)),f.x),
		f.y);
}

float fbm(vec2 p)
{
	float v = 0.0;
	v += noise(p*1.)*.5;
	v += noise(p*2.)*.25;
	v += noise(p*4.)*.125;
	return v;
}

void main()
{
    vec2 uv = texUV;

    vec4 src = texture(u_tex, uv);

    if(rand(vec2(u_seed, 0.0f)) < 0.25f)
        uv = 1 - uv;
    else if(rand(vec2(u_seed, 0.0f)) < 0.50f)
        uv.y = 1 - uv.y;
    else if(rand(vec2(u_seed, 0.0f)) < 0.75f)
        uv.x = 1 - uv.x;

    uv.x -= 1.5;

    vec4 col = src;

    float ctime = u_time * 2.0f;

    float d = uv.x + uv.y * 0.5f + 0.5 * fbm(uv * 15.1f) + ctime;
    if(d > 0.35)
        col = clamp(col - (d - 0.35f) * 10.0f, 0.0f, 1.0f);

    if(d > 0.47 && d < 0.5) {
        col += (d - 0.4f) * 33.0f * 0.5f * noise(100.0f * uv + vec2(-ctime * 2.0f, 0.0f)) * vec4(1.0f, 0.5f, 0.2f, 1.0f);
    }

    gl_FragColor = col;
}