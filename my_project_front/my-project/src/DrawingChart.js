import * as d3 from 'd3';

function drawingChart (chartData) {
    try {
        var maxIndex = ((chartData.length) - 1);
        var maxStockPrices = 0;
        var minStockPrices = 999999999999;
        for (let i = 0; i < chartData.length; i++) {
            if (chartData[i][1] < minStockPrices) {
                minStockPrices = chartData[i][1];
            }
            if (chartData[i][4] > maxStockPrices) {
                maxStockPrices = chartData[i][4];
            }
        }
        alert('chartData 받아오기 성공');
        /*
        X, Y축 그리기
        나중에 이걸 동적으로 활용하고 싶으면 화면에서 range값을 받아오면 동적으로 활용가능하겠다.
        domain 은 데이터의 일반적으로 최소, 최대값으로 설정하고 range 는 표출할 범위의 너비, 높이 픽셀값!!
        */
        const xScale = d3.scaleBand().domain([chartData[0][0], chartData[maxIndex][0]]).range([20, 660]).padding(0.2);
        const yScale = d3.scaleLinear().domain([minStockPrices, maxStockPrices]).range([330, 20]);
        /*
        위에서 만든 축을 활용해 HTML태그 만들기
        svg 안에 g 태그를 생성한다.
        g 태그는 svg 태그 안에서 여러 요소들을 그룹화 하는데 사용하는 태그
        축에 사용되는 여러 막대기나 텍스트들의 집합을 묶어줄 g 태그가 필요
            x에만 attr이 붙는 이유는 기본적으로 SVG 내부에서 좌표계는 y값이 높을수록 아래로 향하기 때문에 x축의 위치를 변경 #
            translate 를 이용해서 y축에 대응하는 x값의 위치를 330으로 수정
        */
        const xAxisSVG = d3.select('svg').append('g').attr('transform', 'translate(0, 330)');
        const yAxisSVG = d3.select('svg').append('g');
        /*
        AXIS함수 만들기
        d3 에서는 완성된 형태의 축을 바로 생성할 수 있는 axis 함수를 제공
        axis* 계열의 함수는 axisBottom, axisTop, axisRight, axisLeft 가 있는데, 기억하기 쉽게 axis 뒤에 막대기가 튀어나올 방향을 지정하면 된다고 생각하면 쉽다.
        tickSize는 축마다 달려있는 막대기들을 tick 이라고 하는데, 이 tick의 높이값을 설정(10이면 10픽셀)
        ticks 는 막대기들이 축에 분포될 양을 설정(10이라고 해서 10개가 분포될 것 같지만 그렇지 않고 함수 내부의 알고리즘에 의해 적절한 개수로 배치)
        */
        const xAxis = d3.axisBottom(xScale).tickSize(10).ticks(10);
        const yAxis = d3.axisRight(yScale).tickSize(10).ticks(10);
        xAxis(xAxisSVG);
        yAxis(yAxisSVG);
        alert('chart틀 만들기 성공');
        // 봉차트를 생성한다.
        for (let i = 0; i < chartData.length; i++) {
            const cData = chartData[i];
            const g = d3.select('svg').append('g')
                .attr('stroke-linecap', 'round')
                .attr('stroke', 'black')
                // 1. SVG 태그 안에 있는 g태그를 모두 찾는다.
                .selectAll('g')
                // 2. 찾은 요소에 데이터를 씌운다.
                .data(cData)
                // 3. 찾은요소가 더 많은 경우 기존 G와 join한다.
                .join('g')
                // 4. 각 봉이 생성될 위치를 지정해준다.
                .attr('transform', cData => `translate(${xScale(cData[0])},0)`);
            g.append('line')
                .attr('y1', cData => yScale(cData[1]))
                .attr('y2', cData => yScale(cData[4]));
            g.append('line')
                .attr('y1', cData => yScale(cData[2]))
                .attr('y2', cData => yScale(cData[3]))
                .attr('stroke-width', xScale.bandwidth())
                .attr('stroke', cData => cData[2] > cData[3] ? d3.schemeSet1[0] : cData[3] > cData[2] ? d3.schemeSet1[2] : d3.schemeSet1[8]);
            g.append('title')
                .text(cData => `${cData[0]}
                Open: ${cData[2]}
                Close: ${cData[3]}
                Low: ${cData[1]}
                High: ${cData[4]}`);
        }
        alert('chart 봉 만들기 성공');
    } catch (e) {
        alert('차트를 불러오는 도중 다음과 같은 에러가 발생하였습니다 \n' + e.name + '\n' + e.message);
        return false;
    }
    return true;
}
