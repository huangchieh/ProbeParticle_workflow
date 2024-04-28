for type in 1 #2
do 
	cd $type
	echo Processing $type
	python ../ProbeParticleModel-complix_tip/plot_results.py --df &&
	python ../ProbeParticleModel-complix_tip/plot_results.py --df --atoms
	cd ..
done
