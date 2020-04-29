# Literature Review

## Hao (Shanghai)

### Questions asked:

- Does the current ambulance stations meet the predetermined stardards?
- Is there a Feasible Solution of 8 Ambulance Stations?

### Model

![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao1.png)
![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao2.png)
![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao3.png)
![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao4.png)
![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao5.png)
![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao6.png)

5.1.1._Demand Points_.Organized the county into 2-kilometer ∗ 2-kilometer square nodes with Arcgis 10.2 so ware. is gives us a total of 187 demand nodes and we assumed that the ambulances can be posted in any one of the nodes except in the nodes that make up the boundary.

5.1.2. _Demand Scenarios_. To re ect the realistic demands, EMS calls would be further classi ed based on their time and date. Days are classified into workdays (Monday through Friday) and o -days (weekends and holidays) and the call times are arranged into four periods of a single day: (i) dawn (00:00 AM–6:00 AM), (ii) morning (6:00 AM–12:00 PM), (iii) a ernoon (12:00 PM–18:00 PM), and (iv) evening (18:00 PM–24:00 PM). e number of emergency calls of the patients in each of these 8 scenarios is shown in Table 1.

5.1.3. _Potential Ambulance Station Locations and the Hospital Locations_. We selected a total of 17 potential ambulance location sites in the city of Songjiang including the hospitals and community health service centers. e current 8 ambu- lance stations are also in our potential location sites and we add the remaining potential stations in each administrative region mentioned in the previous context. All the potential ambulance stations’ information in detail can be seen in Fig- ure 2 and Table 2. From the detailed emergency call records, we nd that there are more than 50 hospitals that are the potential destination hospitals. But some hospitals received the amount of patients in single digit in the whole year. Finally, we select 29 hospitals as the destination hospitals, each of which has received more than ten patients according to the emergency call records. Table 3 shows the detailed coordinates data for these hospitals. All the geographic coor- dinates of these potential stations and hospitals are obtained from the Baidu API with JAVA program; then we convert them into WGS-84 coordinates through Arcgis 10.2 so ware.

![alt text](https://github.com/gabrielsaruhashi/ER-Bhutan/blob/master/papers/assets/hao7.png)

## (Dhaka)

### Questions asked:

- Should di↵erent outpost locations be used for di↵erent times of day
- What performance improvements are possible by optimizing outpost locations?

### Optimization Approach
