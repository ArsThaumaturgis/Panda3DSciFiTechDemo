#version 130

in vec2 texCoord;

uniform sampler2D sourceTex1;
uniform sampler2D sourceTex2;
uniform float startTime;
uniform float duration;
uniform float randomisation1;
uniform float randomisation2;

uniform float osg_FrameTime;

out vec4 color;

void main()
{
    float timeVal = (osg_FrameTime - startTime) / duration;

    vec4 noisePix1 = texture(sourceTex1, ((normalize(texCoord) * (0.05 + timeVal*0.01) + randomisation1)));

    float value = noisePix1.x;

    float dist = min(0.8, length(texCoord));
    dist += value * 0.6;

    float growthVal = 1 - sin(timeVal * 3.142);
    growthVal = growthVal * 0.8 + 0.2;

    float alpha = smoothstep(0.8 * growthVal, 1 * growthVal, 1 - dist);
    //alpha *= 1 - smoothstep(0.8, 1, timeVal);

    float colourVal = 1 - min(1, dist * growthVal / 0.3);
    colourVal += sin((length(texCoord) + value) * 10 + timeVal * 10) * 0.4;
    colourVal = clamp(colourVal, 0, 1);
    vec3 colour = vec3(1, colourVal, colourVal) * alpha;

    color.xyz = colour;
    color.w = 1;
}