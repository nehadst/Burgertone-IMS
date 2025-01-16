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

// Mapping for item name standardization
const itemMapping = {
    'Classic Combo': 'Classic',
    'Classic Burger': 'Classic',
    'Classic Meal Deal': 'Classic',
    'Classic Burger Combo': 'Classic',
    'Classic Burger Combo 1': 'Classic',
    'Classic Burger Combo 2': 'Classic',
    
    'Jazz Combo': 'Jazz',
    'Jazz Burger': 'Jazz',
    'Jazz Burger Combo': 'Jazz',
    'Jazz Meal Deal': 'Jazz',
    
    'Country Combo': 'Country',
    'Country Burger': 'Country',
    'Country Burger Combo': 'Country',
    'Country Meal Deal': 'Country',
    
    'Rock Combo': 'Rock',
    'Rock Burger': 'Rock',
    'Rock Burger Combo': 'Rock',
    'Rock Meal Deal': 'Rock',
    
    'Family Meal': 'Family Meal',
    'Family Meal 2.0': 'Family Meal',
    'Family Meal Deal': 'Family Meal'
};

const Dashboard = () => {
    const { data: rawPredictions, isLoading, error } = useQuery({
        queryKey: ['predictions'],
        queryFn: async () => {
            console.log("Fetching predictions...");
            const response = await axios.get('http://localhost:8000/api/inventory/predictions/7');
            console.log("Raw API response:", response.data);
            return response.data;
        }
    });

    // Combine similar items' predictions
    const predictions = React.useMemo(() => {
        if (!rawPredictions) {
            console.log("No raw predictions data");
            return null;
        }

        console.log("Processing raw predictions:", rawPredictions);
        const combinedPredictions = {};

        rawPredictions.forEach(item => {
            console.log("Processing item:", item);
            // Get standardized name
            const standardName = itemMapping[item.item_name] || item.item_name;
            console.log("Standardized name:", standardName);

            if (!combinedPredictions[standardName]) {
                combinedPredictions[standardName] = {
                    item_name: standardName,
                    predictions: item.predictions.map(p => ({ ...p })),
                    historical_avg: item.historical_avg,
                    count: 1
                };
            } else {
                // Combine predictions
                item.predictions.forEach((pred, index) => {
                    combinedPredictions[standardName].predictions[index].predicted_quantity += 
                        pred.predicted_quantity;
                });
                combinedPredictions[standardName].historical_avg = 
                    (combinedPredictions[standardName].historical_avg * combinedPredictions[standardName].count + 
                     item.historical_avg) / (combinedPredictions[standardName].count + 1);
                combinedPredictions[standardName].count++;
            }
        });

        console.log("Combined predictions:", combinedPredictions);
        return Object.values(combinedPredictions);
    }, [rawPredictions]);

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