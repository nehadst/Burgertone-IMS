import React from 'react';
import { 
    Container, 
    Grid, 
    Paper, 
    Typography, 
    Box,
    CircularProgress,
    Card,
    CardContent
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { 
    LineChart, 
    Line, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip, 
    Legend,
    ResponsiveContainer 
} from 'recharts';

const Dashboard = () => {
    const { data: predictions, isLoading, error } = useQuery({
        queryKey: ['predictions'],
        queryFn: async () => {
            const response = await axios.get('http://localhost:8000/api/inventory/predictions/7');
            return response.data;
        }
    });

    if (isLoading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <Typography color="error">Error loading predictions: {error.message}</Typography>
            </Box>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" gutterBottom align="center" sx={{ mb: 4 }}>
                Inventory Predictions Dashboard
            </Typography>
            
            <Grid container spacing={3}>
                {predictions && predictions.map((item) => (
                    <Grid item xs={12} md={6} key={item.item_name}>
                        <Card elevation={3}>
                            <CardContent>
                                <Typography variant="h5" gutterBottom>
                                    {item.item_name}
                                </Typography>
                                <Typography color="textSecondary" gutterBottom>
                                    Historical Average: {item.historical_avg.toFixed(1)} units/day
                                </Typography>
                                
                                <Box sx={{ height: 300, mt: 2 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart
                                            data={item.predictions}
                                            margin={{
                                                top: 5,
                                                right: 30,
                                                left: 20,
                                                bottom: 5,
                                            }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis 
                                                dataKey="date" 
                                                tickFormatter={(date) => new Date(date).toLocaleDateString()}
                                            />
                                            <YAxis />
                                            <Tooltip 
                                                labelFormatter={(date) => new Date(date).toLocaleDateString()}
                                                formatter={(value) => [`${value} units`, "Predicted Quantity"]}
                                            />
                                            <Legend />
                                            <Line
                                                type="monotone"
                                                dataKey="predicted_quantity"
                                                stroke="#8884d8"
                                                name="Predicted Quantity"
                                                strokeWidth={2}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default Dashboard; 