import { Grid } from "@mui/material";
import TimeSeriesPanel from "components/metrics/panels/TimeSeriesPanel";
import dayjs from "dayjs";
import { RocksetParam } from "lib/rockset";
import { useState } from "react";

const ROW_HEIGHT = 240;

export default function Kpis() {
    // Looking at data from the past six months
    const [startTime, setStartTime] = useState(dayjs().subtract(6, 'month'));
    const [stopTime, setStopTime] = useState(dayjs());

    const timeParams: RocksetParam[] = [
        {
        name: "startTime",
        type: "string",
        value: startTime,
        },
        {
        name: "stopTime",
        type: "string",
        value: stopTime,
        },
    ];

    // deprecate this in Q3 2023
    const contributionTimeParams: RocksetParam[] = [
        {
        name: "startTime",
        type: "string",
        value: "2022-07-03T00:00:00.000Z",
        },
        {
        name: "stopTime",
        type: "string",
        value: stopTime,
        },
    ];

    return (
        <Grid container spacing={2}>
            <Grid item xs={12} lg={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                title={"Avg Time To Signal - E2E (Weekly)"}
                queryName={"time_to_signal"}
                queryCollection={"pytorch_dev_infra_kpis"}
                queryParams={[
                    {
                        name: "buildOrAll",
                        type: "string",
                        value: "all",
                    },
                    ...timeParams,
                ]}
                granularity={"week"}
                timeFieldName={"week_bucket"}
                yAxisFieldName={"avg_tts"}
                yAxisLabel={"Hours"}
                yAxisRenderer={(unit) => `${unit}`}
                />
            </Grid>

            <Grid item xs={12} lg={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                title={"# of Reverts/week (2 week moving avg)"}
                queryName={"num_reverts"}
                queryCollection={"pytorch_dev_infra_kpis"}
                queryParams={[
                    ...timeParams,
                ]}
                granularity={"week"}
                timeFieldName={"bucket"}
                yAxisFieldName={"num"}
                yAxisRenderer={(unit) => `${unit}`}
                groupByFieldName={"code"}
                />
            </Grid>

            <Grid item xs={12} lg={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                title={"% of Commits Red on Trunk (Weekly)"}
                queryName={"master_commit_red_percent"}
                queryCollection={"metrics"}
                queryParams={[
                    ...timeParams,
                ]}
                granularity={"week"}
                timeFieldName={"granularity_bucket"}
                yAxisFieldName={"red"}
                yAxisRenderer={(unit) => {
                    return `${unit * 100} %`;
                }}
                />
            </Grid>

            <Grid item xs={12} lg={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                title={"# of Force Merges (Weekly)"}
                queryName={"number_of_force_pushes_historical"}
                queryCollection={"pytorch_dev_infra_kpis"}
                queryParams={[
                    ...timeParams,
                ]}
                granularity={"week"}
                timeFieldName={"bucket"}
                yAxisFieldName={"count"}
                yAxisRenderer={(unit) => `${unit}`}
                />
            </Grid>
            <Grid item xs={12} lg={6} height={ROW_HEIGHT}>
              <TimeSeriesPanel
                title={"viable/strict Lag (Daily)"}
                queryName={"strict_lag_historical"}
                queryCollection={"pytorch_dev_infra_kpis"}
                queryParams={[...timeParams]}
                granularity={"day"}
                timeFieldName={"push_time"}
                yAxisFieldName={"diff_hr"}
                yAxisLabel={"Hours"}
                yAxisRenderer={(unit) => `${unit}`}
                // the data is very variable, so set the y axis to be something that makes this chart a bit easier to read
                additionalOptions={{ yAxis: { max: 7 } }}
              />
            </Grid>
            <Grid item xs={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                    title={"External PR Count (Weekly with 4 week moving average)"}
                    queryName={"external_contribution_stats"}
                    queryParams={[...contributionTimeParams]}
                    queryCollection={"metrics"}
                    granularity={"week"}
                    timeFieldName={"granularity_bucket"}
                    yAxisFieldName={"pr_count"}
                    yAxisRenderer={(value) => value}
                    additionalOptions={{ yAxis: { scale: true } }}
                />
            </Grid>

            <Grid item xs={6} height={ROW_HEIGHT}>
                <TimeSeriesPanel
                    title={"Monthly External PR Count"}
                    queryName={"monthly_contribution_stats"}
                    queryCollection={"pytorch_dev_infra_kpis"}
                    queryParams={[...contributionTimeParams]}
                    granularity={"month"}
                    timeFieldName={"year_and_month"}
                    yAxisFieldName={"pr_count"}
                    yAxisRenderer={(value) => value}
                    additionalOptions={{ yAxis: { scale: true } }}
                />
            </Grid>
        </Grid>
    );
}
