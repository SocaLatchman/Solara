const minKw = document.querySelectorAll('.low');
const maxKw = document.querySelectorAll('.high');
const current = document.querySelectorAll('.current');
const solarArrayCount = document.querySelectorAll('.card');

//circle
function renderCircleGraphic(){
    const circleSize = 400;
    const centerX = circleSize / 2; 
    const centerY = 160;

    const startAngle = 0;
    const endAngle = Math.PI * 2;
    const totalAngle = endAngle - startAngle;

    for(let j = 0; j<solarArrayCount.length; j++) {
      const circleColorScale = d3.scaleSequential()
          .domain([minKw[j].innerHTML, maxKw[j].innerHTML])
          .interpolator(d3.interpolateLab('#64C082', '#FEFEFE'));

       const circleSvg = d3.selectAll('.energy-dial');
       const circleGroup = circleSvg.append('g')
            .attr('transform', `translate(${centerX}, ${centerY})`);

       const segmentCount = 80;
       const arcGenerator = d3.arc()
            .innerRadius(125)
            .outerRadius(130)
            .cornerRadius(0);

       for(let i = 0; i<segmentCount; i++) {
          const startSegment = startAngle + (i / segmentCount) * totalAngle;
          const endSegment = startAngle + ((i + 1) / segmentCount) * totalAngle;
          const progressFraction = i / (segmentCount - 1);
          const circlekWValue = minKw[j].innerHTML + progressFraction * (maxKw[j].innerHTML - minKw[j].innerHTML);

          circleGroup.append('path')
              .attr('d', arcGenerator({ startAngle: startSegment, endAngle: endSegment}))
              .attr('fill', circleColorScale(circlekWValue));
           }
   }
}








//bar

const barSvg = d3.select('#status-bar-gradient');
const barColorScale = d3.scaleSequential()
   .domain([minKw, maxKw])
   .interpolator(d3.interpolateLab('#63C082', '#22F369'));

const gradientDefs = barSvg.append('defs');
const linearGradient = gradientDefs.append('linearGradient')
    .attr('id', 'solar-gradient')
    .attr('x1', '0%').attr('y1', '0%')
    .attr('x2', '100%').attr('y2', '0%');

const colorStops = 10;
for(let i = 0; i<colorStops; i++) {
    const offset = i / (colorStops - 1);
    const kwValue = minKw + offset * (maxKw - minKw);
    linearGradient.append('stop')
        .attr('offset', `${offset * 100}%`)
        .attr('stop-color', barColorScale(kwValue));
}

barSvg.append('rect')
   .attr('class', 'solar-bar-rect') 
   .attr('rx', 6)
   .attr('ry', 6)
   .attr('fill', 'url(#solar-gradient)');

const marker = barSvg.append('g')
    .attr('class', 'marker')
    .attr('transform', 'translate(0, 0)')

marker.append('line')
   .attr('x1', 0)
   .attr('y1', 0)
   .attr('x2', 0)
   .attr('y2', 30)
   .attr('stroke', '#ce2828')
   .attr('stroke-width', 10)


renderCircleGraphic();