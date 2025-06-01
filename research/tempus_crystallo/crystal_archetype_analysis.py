#!/usr/bin/env python3
"""
TEMPUS-CRYSTALLO Phase 0.1: Crystal Archetype Derivation
Empirically derive crystal archetypes from TC.1.3 mock data and establish
mathematical definitions for 'Stable', 'Growth', and 'Decay' classifications.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CrystalArchetypeAnalyzer:
    """Derives empirical crystal archetypes from temporal crystal data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.archetype_models = {}
        self.archetype_definitions = {}
        self.performance_thresholds = {}
        
    def generate_tc13_mock_data(self, n_crystals=1000):
        """Generate expanded mock data based on TC.1.3 findings"""
        np.random.seed(42)  # Reproducible results
        
        # Create three distinct crystal populations based on TC.1.3 archetypes
        n_stable = int(n_crystals * 0.4)  # 40% stable (high success)
        n_growth = int(n_crystals * 0.35)  # 35% growth (medium success) 
        n_decay = int(n_crystals * 0.25)   # 25% decay (low success)
        
        crystals = []
        
        # Stable Crystal Archetype (High Success: 85-95%)
        for i in range(n_stable):
            crystal = {
                'crystal_id': f'stable_{i}',
                'fractal_dimension': np.random.normal(2.45, 0.15),  # Higher fractal complexity
                'lyapunov_exponent': np.random.normal(-0.3, 0.1),  # Stable dynamics
                'surface_roughness': np.random.normal(0.2, 0.05),  # Smooth surfaces
                'phonon_mode_count': np.random.randint(15, 25),    # Rich resonance
                'quantum_coherence': np.random.normal(0.88, 0.08), # High coherence
                'compression_efficiency': np.random.normal(0.75, 0.1), # Good compression
                'crystallization_energy': np.random.normal(3.2, 0.4), # Moderate energy
                'defect_density': np.random.normal(0.12, 0.04),    # Low defects
                'growth_rate': np.random.normal(0.15, 0.05),       # Slow, steady growth
                'stability_index': np.random.normal(0.85, 0.1),    # High stability
                'task_success_rate': np.random.normal(0.90, 0.05), # High success
                'true_archetype': 'Stable'
            }
            crystals.append(crystal)
            
        # Growth Crystal Archetype (Medium Success: 60-80%)
        for i in range(n_growth):
            crystal = {
                'crystal_id': f'growth_{i}',
                'fractal_dimension': np.random.normal(2.8, 0.2),   # Very high complexity
                'lyapunov_exponent': np.random.normal(0.1, 0.15),  # Slightly unstable
                'surface_roughness': np.random.normal(0.35, 0.1),  # Rougher surfaces
                'phonon_mode_count': np.random.randint(20, 35),    # Very rich resonance
                'quantum_coherence': np.random.normal(0.72, 0.12), # Medium coherence
                'compression_efficiency': np.random.normal(0.65, 0.15), # Decent compression
                'crystallization_energy': np.random.normal(4.1, 0.6), # Higher energy
                'defect_density': np.random.normal(0.25, 0.08),    # Medium defects
                'growth_rate': np.random.normal(0.45, 0.15),       # Rapid growth
                'stability_index': np.random.normal(0.65, 0.15),   # Medium stability
                'task_success_rate': np.random.normal(0.70, 0.10), # Medium success
                'true_archetype': 'Growth'
            }
            crystals.append(crystal)
            
        # Decay Crystal Archetype (Low Success: 30-50%)
        for i in range(n_decay):
            crystal = {
                'crystal_id': f'decay_{i}',
                'fractal_dimension': np.random.normal(1.9, 0.2),   # Lower complexity
                'lyapunov_exponent': np.random.normal(0.4, 0.2),   # Unstable dynamics
                'surface_roughness': np.random.normal(0.55, 0.15), # Very rough
                'phonon_mode_count': np.random.randint(5, 15),     # Poor resonance
                'quantum_coherence': np.random.normal(0.45, 0.15), # Low coherence
                'compression_efficiency': np.random.normal(0.35, 0.15), # Poor compression
                'crystallization_energy': np.random.normal(2.1, 0.5), # Low energy
                'defect_density': np.random.normal(0.45, 0.12),    # High defects
                'growth_rate': np.random.normal(-0.05, 0.1),       # Decay/shrinkage
                'stability_index': np.random.normal(0.35, 0.15),   # Low stability
                'task_success_rate': np.random.normal(0.40, 0.10), # Low success
                'true_archetype': 'Decay'
            }
            crystals.append(crystal)
            
        return pd.DataFrame(crystals)
    
    def analyze_archetype_clusters(self, df):
        """Perform unsupervised clustering to discover natural archetypes"""
        
        # Select crystal properties for clustering (exclude IDs and targets)
        feature_cols = [
            'fractal_dimension', 'lyapunov_exponent', 'surface_roughness',
            'phonon_mode_count', 'quantum_coherence', 'compression_efficiency',
            'crystallization_energy', 'defect_density', 'growth_rate', 'stability_index'
        ]
        
        X = df[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Test different clustering approaches
        clustering_results = {}
        
        # K-Means with different k values
        silhouette_scores = []
        k_range = range(2, 8)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(score)
            
            if k == 3:  # Our target number of archetypes
                clustering_results['kmeans_3'] = {
                    'model': kmeans,
                    'labels': cluster_labels,
                    'silhouette_score': score,
                    'inertia': kmeans.inertia_
                }
        
        # DBSCAN for density-based clustering
        dbscan = DBSCAN(eps=0.5, min_samples=10)
        dbscan_labels = dbscan.fit_predict(X_scaled)
        n_clusters_dbscan = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
        
        if n_clusters_dbscan > 1:
            clustering_results['dbscan'] = {
                'model': dbscan,
                'labels': dbscan_labels,
                'n_clusters': n_clusters_dbscan,
                'n_noise': list(dbscan_labels).count(-1)
            }
        
        return clustering_results, silhouette_scores, feature_cols
    
    def derive_archetype_definitions(self, df, clustering_result, feature_cols):
        """Derive mathematical definitions for each discovered archetype"""
        
        labels = clustering_result['labels']
        df_with_clusters = df.copy()
        df_with_clusters['predicted_cluster'] = labels
        
        archetype_definitions = {}
        
        # Analyze each cluster
        unique_clusters = sorted(set(labels))
        cluster_names = ['Stable', 'Growth', 'Decay']  # Map to meaningful names
        
        for i, cluster_id in enumerate(unique_clusters):
            if i >= len(cluster_names):
                cluster_name = f'Unknown_{i}'
            else:
                cluster_name = cluster_names[i]
                
            cluster_data = df_with_clusters[df_with_clusters['predicted_cluster'] == cluster_id]
            
            # Calculate statistical boundaries for this archetype
            definition = {
                'cluster_id': cluster_id,
                'archetype_name': cluster_name,
                'sample_count': len(cluster_data),
                'success_rate_mean': cluster_data['task_success_rate'].mean(),
                'success_rate_std': cluster_data['task_success_rate'].std(),
                'feature_bounds': {},
                'classification_rules': {}
            }
            
            # Define feature boundaries (mean ± 2*std for 95% coverage)
            for feature in feature_cols:
                values = cluster_data[feature]
                definition['feature_bounds'][feature] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min_bound': float(values.mean() - 2*values.std()),
                    'max_bound': float(values.mean() + 2*values.std()),
                    'percentile_25': float(values.quantile(0.25)),
                    'percentile_75': float(values.quantile(0.75))
                }
            
            # Create classification rules based on most discriminative features
            definition['classification_rules'] = self._create_classification_rules(
                cluster_data, feature_cols
            )
            
            archetype_definitions[cluster_name] = definition
        
        return archetype_definitions
    
    def _create_classification_rules(self, cluster_data, feature_cols):
        """Create IF-THEN rules for archetype classification"""
        
        rules = {}
        
        # Find most discriminative features for this cluster
        for feature in feature_cols:
            values = cluster_data[feature]
            rules[feature] = {
                'typical_range': (
                    float(values.quantile(0.25)), 
                    float(values.quantile(0.75))
                ),
                'confidence_threshold': float(values.mean()),
                'strength': float(values.std())  # Lower std = more characteristic
            }
        
        # Create compound rules
        key_features = sorted(rules.keys(), key=lambda x: rules[x]['strength'])[:3]
        
        compound_rule = " AND ".join([
            f"{feat} IN [{rules[feat]['typical_range'][0]:.3f}, {rules[feat]['typical_range'][1]:.3f}]"
            for feat in key_features
        ])
        
        rules['compound_classification_rule'] = compound_rule
        rules['key_discriminative_features'] = key_features
        
        return rules
    
    def validate_archetype_predictions(self, df, archetype_definitions):
        """Validate how well derived archetypes predict task success"""
        
        predictions = []
        true_success_rates = []
        
        for _, row in df.iterrows():
            # Classify this crystal based on archetype definitions
            best_match = None
            best_score = -1
            
            for archetype_name, definition in archetype_definitions.items():
                score = self._calculate_archetype_match_score(row, definition)
                if score > best_score:
                    best_score = score
                    best_match = archetype_name
            
            predictions.append(best_match)
            true_success_rates.append(row['task_success_rate'])
        
        df_results = pd.DataFrame({
            'predicted_archetype': predictions,
            'true_archetype': df['true_archetype'],
            'actual_success_rate': true_success_rates
        })
        
        # Calculate prediction accuracy
        accuracy = (df_results['predicted_archetype'] == df_results['true_archetype']).mean()
        
        # Calculate success rate prediction error
        archetype_success_means = {}
        for archetype in archetype_definitions.keys():
            mask = df_results['predicted_archetype'] == archetype
            if mask.sum() > 0:
                archetype_success_means[archetype] = df_results[mask]['actual_success_rate'].mean()
        
        return {
            'classification_accuracy': accuracy,
            'archetype_success_rates': archetype_success_means,
            'prediction_results': df_results
        }
    
    def _calculate_archetype_match_score(self, crystal_row, archetype_definition):
        """Calculate how well a crystal matches an archetype definition"""
        
        scores = []
        
        for feature, bounds in archetype_definition['feature_bounds'].items():
            if feature in crystal_row:
                value = crystal_row[feature]
                mean = bounds['mean']
                std = bounds['std']
                
                # Calculate normalized distance from archetype center
                if std > 0:
                    distance = abs(value - mean) / std
                    score = max(0, 1 - distance/2)  # Score decreases with distance
                    scores.append(score)
        
        return np.mean(scores) if scores else 0
    
    def visualize_archetype_analysis(self, df, clustering_result, archetype_definitions):
        """Create comprehensive visualizations of archetype analysis"""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Crystal Archetype Analysis Results', fontsize=16)
        
        # 1. PCA visualization of clusters
        feature_cols = [
            'fractal_dimension', 'lyapunov_exponent', 'surface_roughness',
            'phonon_mode_count', 'quantum_coherence', 'compression_efficiency',
            'crystallization_energy', 'defect_density', 'growth_rate', 'stability_index'
        ]
        
        X = df[feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        scatter = axes[0,0].scatter(X_pca[:, 0], X_pca[:, 1], 
                                  c=clustering_result['labels'], 
                                  cmap='viridis', alpha=0.7)
        axes[0,0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        axes[0,0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        axes[0,0].set_title('Crystal Clusters in PCA Space')
        plt.colorbar(scatter, ax=axes[0,0])
        
        # 2. Success rate by archetype
        df_with_clusters = df.copy()
        df_with_clusters['predicted_cluster'] = clustering_result['labels']
        
        archetype_names = list(archetype_definitions.keys())
        success_by_archetype = []
        
        for i, name in enumerate(archetype_names):
            cluster_data = df_with_clusters[df_with_clusters['predicted_cluster'] == i]
            if len(cluster_data) > 0:
                success_by_archetype.append(cluster_data['task_success_rate'].values)
            else:
                success_by_archetype.append([])
        
        axes[0,1].boxplot(success_by_archetype, labels=archetype_names)
        axes[0,1].set_ylabel('Task Success Rate')
        axes[0,1].set_title('Success Rate Distribution by Archetype')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Feature importance heatmap
        feature_importance = np.zeros((len(archetype_names), len(feature_cols)))
        
        for i, archetype_name in enumerate(archetype_names):
            definition = archetype_definitions[archetype_name]
            for j, feature in enumerate(feature_cols):
                if feature in definition['feature_bounds']:
                    # Use inverse of std as importance (lower std = more characteristic)
                    std = definition['feature_bounds'][feature]['std']
                    feature_importance[i, j] = 1 / (std + 0.01)  # Avoid division by zero
        
        im = axes[0,2].imshow(feature_importance, cmap='YlOrRd', aspect='auto')
        axes[0,2].set_xticks(range(len(feature_cols)))
        axes[0,2].set_xticklabels(feature_cols, rotation=45, ha='right')
        axes[0,2].set_yticks(range(len(archetype_names)))
        axes[0,2].set_yticklabels(archetype_names)
        axes[0,2].set_title('Feature Discriminative Power by Archetype')
        plt.colorbar(im, ax=axes[0,2])
        
        # 4. Archetype stability analysis
        for i, archetype_name in enumerate(archetype_names):
            cluster_data = df_with_clusters[df_with_clusters['predicted_cluster'] == i]
            if len(cluster_data) > 0:
                axes[1,0].scatter(cluster_data['stability_index'], 
                                cluster_data['task_success_rate'],
                                label=archetype_name, alpha=0.7)
        
        axes[1,0].set_xlabel('Stability Index')
        axes[1,0].set_ylabel('Task Success Rate')
        axes[1,0].set_title('Stability vs Success by Archetype')
        axes[1,0].legend()
        
        # 5. Growth rate analysis
        for i, archetype_name in enumerate(archetype_names):
            cluster_data = df_with_clusters[df_with_clusters['predicted_cluster'] == i]
            if len(cluster_data) > 0:
                axes[1,1].scatter(cluster_data['growth_rate'], 
                                cluster_data['defect_density'],
                                label=archetype_name, alpha=0.7)
        
        axes[1,1].set_xlabel('Growth Rate')
        axes[1,1].set_ylabel('Defect Density')
        axes[1,1].set_title('Growth vs Defects by Archetype')
        axes[1,1].legend()
        
        # 6. Quantum coherence distribution
        coherence_by_archetype = []
        for i, name in enumerate(archetype_names):
            cluster_data = df_with_clusters[df_with_clusters['predicted_cluster'] == i]
            if len(cluster_data) > 0:
                coherence_by_archetype.append(cluster_data['quantum_coherence'].values)
            else:
                coherence_by_archetype.append([])
        
        axes[1,2].hist(coherence_by_archetype, bins=20, alpha=0.7, 
                      label=archetype_names, density=True)
        axes[1,2].set_xlabel('Quantum Coherence')
        axes[1,2].set_ylabel('Density')
        axes[1,2].set_title('Quantum Coherence Distribution')
        axes[1,2].legend()
        
        plt.tight_layout()
        return fig
    
    def generate_archetype_report(self, df, clustering_results, archetype_definitions, validation_results):
        """Generate comprehensive archetype analysis report"""
        
        report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'dataset_size': len(df),
                'clustering_method': 'K-Means (k=3)',
                'feature_count': 10
            },
            'clustering_quality': {
                'silhouette_score': clustering_results['kmeans_3']['silhouette_score'],
                'inertia': clustering_results['kmeans_3']['inertia']
            },
            'archetype_definitions': archetype_definitions,
            'validation_results': {
                'classification_accuracy': validation_results['classification_accuracy'],
                'archetype_success_prediction': validation_results['archetype_success_rates']
            },
            'key_findings': self._generate_key_findings(archetype_definitions, validation_results),
            'implementation_recommendations': self._generate_implementation_recommendations(
                archetype_definitions, validation_results
            )
        }
        
        return report
    
    def _generate_key_findings(self, archetype_definitions, validation_results):
        """Generate key insights from archetype analysis"""
        
        findings = []
        
        # Success rate analysis
        success_rates = validation_results['archetype_success_rates']
        if success_rates:
            best_archetype = max(success_rates.keys(), key=lambda x: success_rates[x])
            worst_archetype = min(success_rates.keys(), key=lambda x: success_rates[x])
            
            findings.append(f"'{best_archetype}' archetype shows highest success rate: {success_rates[best_archetype]:.3f}")
            findings.append(f"'{worst_archetype}' archetype shows lowest success rate: {success_rates[worst_archetype]:.3f}")
        
        # Feature discriminative power
        for archetype_name, definition in archetype_definitions.items():
            key_features = definition['classification_rules']['key_discriminative_features']
            findings.append(f"'{archetype_name}' archetype best identified by: {', '.join(key_features)}")
        
        # Classification accuracy
        accuracy = validation_results['classification_accuracy']
        findings.append(f"Overall archetype classification accuracy: {accuracy:.3f}")
        
        return findings
    
    def _generate_implementation_recommendations(self, archetype_definitions, validation_results):
        """Generate recommendations for TC.2.2 implementation"""
        
        recommendations = []
        
        # Performance optimization
        accuracy = validation_results['classification_accuracy']
        if accuracy > 0.8:
            recommendations.append("High classification accuracy supports production deployment of archetype system")
        else:
            recommendations.append("Consider ensemble methods or additional features to improve classification accuracy")
        
        # Feature selection
        all_key_features = set()
        for definition in archetype_definitions.values():
            all_key_features.update(definition['classification_rules']['key_discriminative_features'])
        
        recommendations.append(f"Prioritize these {len(all_key_features)} discriminative features for real-time classification: {', '.join(all_key_features)}")
        
        # Archetype boundaries
        recommendations.append("Use percentile-based boundaries (25th-75th) for robust archetype classification")
        recommendations.append("Implement confidence scoring based on distance from archetype centers")
        
        # System integration
        recommendations.append("Deploy archetype classification as microservice with <100ms latency requirement")
        recommendations.append("Implement archetype drift detection to monitor classification stability over time")
        
        return recommendations

def main():
    """Run complete archetype analysis pipeline"""
    
    print("🔬 TEMPUS-CRYSTALLO Phase 0.1: Crystal Archetype Analysis")
    print("=" * 60)
    
    analyzer = CrystalArchetypeAnalyzer()
    
    # Generate expanded TC.1.3 mock data
    print("📊 Generating expanded TC.1.3 dataset (1000 crystals)...")
    df = analyzer.generate_tc13_mock_data(1000)
    print(f"   Generated {len(df)} crystal signatures")
    print(f"   Archetype distribution: {df['true_archetype'].value_counts().to_dict()}")
    
    # Perform clustering analysis
    print("\n🎯 Performing unsupervised clustering analysis...")
    clustering_results, silhouette_scores, feature_cols = analyzer.analyze_archetype_clusters(df)
    best_clustering = clustering_results['kmeans_3']
    print(f"   Best clustering silhouette score: {best_clustering['silhouette_score']:.3f}")
    
    # Derive mathematical archetype definitions
    print("\n📐 Deriving mathematical archetype definitions...")
    archetype_definitions = analyzer.derive_archetype_definitions(
        df, best_clustering, feature_cols
    )
    print(f"   Defined {len(archetype_definitions)} crystal archetypes:")
    for name, definition in archetype_definitions.items():
        print(f"     - {name}: {definition['sample_count']} samples, "
              f"success rate {definition['success_rate_mean']:.3f}")
    
    # Validate archetype predictions
    print("\n✅ Validating archetype prediction accuracy...")
    validation_results = analyzer.validate_archetype_predictions(df, archetype_definitions)
    print(f"   Classification accuracy: {validation_results['classification_accuracy']:.3f}")
    print(f"   Success rate predictions: {validation_results['archetype_success_rates']}")
    
    # Generate visualizations
    print("\n📈 Generating archetype analysis visualizations...")
    fig = analyzer.visualize_archetype_analysis(df, best_clustering, archetype_definitions)
    plt.savefig('/home/golde/Tenxsom_AI/research/tempus_crystallo/archetype_analysis_results.png', 
                dpi=300, bbox_inches='tight')
    print("   Saved visualization: archetype_analysis_results.png")
    
    # Generate comprehensive report
    print("\n📋 Generating comprehensive analysis report...")
    report = analyzer.generate_archetype_report(
        df, clustering_results, archetype_definitions, validation_results
    )
    
    # Save results
    with open('/home/golde/Tenxsom_AI/research/tempus_crystallo/archetype_definitions.json', 'w') as f:
        json.dump(archetype_definitions, f, indent=2)
    
    with open('/home/golde/Tenxsom_AI/research/tempus_crystallo/archetype_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("   Saved archetype definitions: archetype_definitions.json")
    print("   Saved analysis report: archetype_analysis_report.json")
    
    # Display key findings
    print("\n🔍 Key Findings:")
    for finding in report['key_findings']:
        print(f"   • {finding}")
    
    print("\n💡 Implementation Recommendations:")
    for rec in report['implementation_recommendations']:
        print(f"   • {rec}")
    
    print(f"\n✨ Phase 0.1 Complete: Empirical archetype definitions established")
    print(f"   Classification accuracy: {validation_results['classification_accuracy']:.1%}")
    print(f"   Ready for Phase 0.2: Crystal Calculation Optimization")

if __name__ == "__main__":
    main()