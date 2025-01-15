import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Card, Grid, Typography } from '@mui/material';

function Dashboard() {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        fetch('/api/inventory/forecast')
            .then(res => res.json())
            .then(data => setData(data));
    }, []);
    
    return (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Card>
                    <Typography variant="h5">Sales Forecast</Typography>
                    {data && (
                        <Line 
                            data={data.predictions}
                            options={{
                                responsive: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'Predicted vs Actual Sales'
                                    }
                                }
                            }}
                        />
                    )}
                </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
                <Card>
                    <Typography variant="h6">AI Insights</Typography>
                    <Typography>{data?.insights}</Typography>
                </Card>
            </Grid>
        </Grid>
    );
}

export default Dashboard; 