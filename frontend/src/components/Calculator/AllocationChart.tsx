import React, { useState } from "react";
import { scaleLinear } from "d3-scale";
import type { CourseAllocation, TimeUnit } from "../../types";
import { formatTimeMinutes, formatTimeHours } from "../../utils/format";

interface AllocationChartProps {
  allocationsA?: CourseAllocation[];
  allocationsB?: CourseAllocation[];
  allocationsC?: CourseAllocation[];
  minFloorMinutes: number;
  unit: TimeUnit;
}

export const AllocationChart: React.FC<AllocationChartProps> = ({ allocationsA = [], allocationsB = [], allocationsC = [], minFloorMinutes, unit }) => {
  const [hoveredCourse, setHoveredCourse] = useState<string | null>(null);
  if (!allocationsA.length && !allocationsB.length) return null;

  const courseNames = allocationsA.map((a) => a.course_name);
  const mapA = new Map(allocationsA.map((a) => [a.course_name, a.minutes]));
  const mapB = new Map(allocationsB.map((b) => [b.course_name, b.minutes]));
  const mapC = new Map(allocationsC.map((c) => [c.course_name, c.minutes]));
  const maxMin = Math.max(...allocationsA.map((a) => a.minutes), ...allocationsB.map((b) => b.minutes), ...allocationsC.map((c) => c.minutes), minFloorMinutes, 60);

  const rowHeight = 52;
  const barHeight = 8;
  const barGap = 4;
  const leftMargin = 155;
  const rightMargin = 90;
  const topMargin = 44;
  const bottomMargin = 42;
  const width = 700;
  const innerWidth = width - leftMargin - rightMargin;
  const height = topMargin + courseNames.length * rowHeight + bottomMargin;

  const xScale = scaleLinear().domain([0, maxMin * 1.15]).range([0, innerWidth]);
  const tickStep = maxMin > 120 ? 30 : 15;
  const ticks: number[] = [];
  for (let t = 0; t <= maxMin * 1.15; t += tickStep) ticks.push(t);

  const formatTickLabel = (mins: number) => (unit === "min" ? `${mins}` : `${(mins / 60).toFixed(1)}h`);
  const formatBarValue = (mins: number) => (unit === "min" ? formatTimeMinutes(mins) : formatTimeHours(mins));
  const hoveredData = hoveredCourse ? { name: hoveredCourse, a: mapA.get(hoveredCourse) || 0, b: mapB.get(hoveredCourse) || 0, c: mapC.get(hoveredCourse) || 0 } : null;
  const minX = xScale(minFloorMinutes);
  const showMinLabelOnAxis = minFloorMinutes > 0 && ticks.every((t) => Math.abs(xScale(t) - minX) > 18);

  return (
    <div style={{ width: "100%", overflowX: "auto" }}>
      <svg role="img" aria-label="Chart comparing time plans across options" viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "auto", display: "block" }}>
        <g transform={`translate(${leftMargin}, 16)`}>
          <rect x={0} y={-10} width={10} height={10} fill="var(--series-a)" />
          <text x={14} y={-1} className="font-label" fill="var(--ink)" fontSize="10">By credits</text>
          <rect x={120} y={-10} width={10} height={10} fill="var(--series-b)" />
          <text x={134} y={-1} className="font-label" fill="var(--ink)" fontSize="10">Credits + difficulty</text>
          {allocationsC.length > 0 && (<><rect x={300} y={-10} width={10} height={10} fill="var(--series-c)" stroke="var(--ink)" strokeWidth="1" /><text x={314} y={-1} className="font-label" fill="var(--ink)" fontSize="10">With breaks</text></>)}
        </g>

        <g transform={`translate(${leftMargin}, ${topMargin})`}>
          {ticks.map((tVal) => {
            const xPos = xScale(tVal);
            return (
              <g key={tVal}>
                <line x1={xPos} y1={0} x2={xPos} y2={courseNames.length * rowHeight} stroke="var(--rule-soft)" strokeWidth="1" />
                <text x={xPos} y={courseNames.length * rowHeight + 18} textAnchor="middle" className="font-figure" fontSize="10" fill="var(--ink-3)">{formatTickLabel(tVal)}</text>
              </g>
            );
          })}

          {minFloorMinutes > 0 && (
            <g>
              <line x1={minX} y1={-6} x2={minX} y2={courseNames.length * rowHeight} stroke="var(--ink)" strokeWidth="1" strokeDasharray="4 3" />
              <text
                x={minX}
                y={showMinLabelOnAxis ? courseNames.length * rowHeight + 34 : -12}
                textAnchor={showMinLabelOnAxis ? "middle" : "start"}
                className="font-label"
                fontSize="9"
                fill="var(--ink)"
              >
                {showMinLabelOnAxis ? "Minimum time" : `Minimum: ${formatTickLabel(minFloorMinutes)}`}
              </text>
            </g>
          )}
        </g>

        {courseNames.map((cName, idx) => {
          const y = topMargin + idx * rowHeight;
          const valA = mapA.get(cName) || 0, valB = mapB.get(cName) || 0, valC = mapC.get(cName) || 0;
          const isHovered = hoveredCourse === cName;
          return (
            <g key={cName} transform={`translate(0, ${y})`} onMouseEnter={() => setHoveredCourse(cName)} onMouseLeave={() => setHoveredCourse(null)} style={{ cursor: "pointer" }}>
              <text x={leftMargin - 12} y={rowHeight / 2 + 3} textAnchor="end" className="font-small" fill="var(--ink)" fontWeight={isHovered ? 600 : 400}>
                {cName.length > 18 ? cName.slice(0, 16) + "…" : cName}
              </text>
              <g transform={`translate(${leftMargin}, 8)`}>
                <rect x={0} y={0} width={Math.max(1, xScale(valA))} height={barHeight} fill="var(--series-a)" />
                <text x={xScale(valA) + 6} y={barHeight - 1} className="font-figure" fontSize="9" fill="var(--ink-3)">{formatBarValue(valA)}</text>

                <rect x={0} y={barHeight + barGap} width={Math.max(1, xScale(valB))} height={barHeight} fill="var(--series-b)" />
                <text x={xScale(valB) + 6} y={barHeight * 2 + barGap - 1} className="font-figure" fontSize="9" fill="var(--accent)" fontWeight={500}>{formatBarValue(valB)}</text>

                {allocationsC.length > 0 && (<>
                  <rect x={0} y={(barHeight + barGap) * 2} width={Math.max(1, xScale(valC))} height={barHeight} fill="var(--series-c)" stroke="var(--ink)" strokeWidth="1" />
                  <text x={xScale(valC) + 6} y={barHeight * 3 + barGap * 2 - 1} className="font-figure" fontSize="9" fill="var(--ink-2)">{formatBarValue(valC)}</text>
                </>)}
              </g>
            </g>
          );
        })}
      </svg>
      <div style={{ marginTop: "10px", minHeight: "22px", borderTop: "1px solid var(--rule-soft)", paddingTop: "8px", color: "var(--ink-2)" }} className="font-small">
        {hoveredData ? (
          <span><b>{hoveredData.name}</b>: By credits {formatBarValue(hoveredData.a)}, Credits + difficulty {formatBarValue(hoveredData.b)}{allocationsC.length > 0 ? `, With breaks ${formatBarValue(hoveredData.c)}` : ""}</span>
        ) : (
          <span style={{ color: "var(--ink-3)" }}>Hover over a course row to see the times for each plan.</span>
        )}
      </div>
    </div>
  );
};
