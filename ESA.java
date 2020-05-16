import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicInteger;

import edu.illinois.cs.cogcomp.descartes.retrieval.IResult;
import edu.illinois.cs.cogcomp.descartes.retrieval.ISearcher;
import edu.illinois.cs.cogcomp.descartes.retrieval.SearcherFactory;

/** Class to parallelize the code to do ESA
 *
 */
class ParallelESA implements Runnable {
  public static ArrayList<String[]> inputs;
  public static ISearcher searcher;
  public static int numConcepts;
  public static AtomicInteger counter = new AtomicInteger(0);

  public ParallelESA(ArrayList<String[]> inputs, ISearcher searcher, int numConcepts){
	this.inputs = inputs;
	this.searcher = searcher;
	this.numConcepts = numConcepts;
  }

  public void run() {
	int index;
	while(counter.get() < inputs.size()) {
	  index = counter.getAndIncrement();
	  String[] input = inputs.get(index);
	  try{
		runTask(input, searcher, numConcepts);
	  } catch(Exception e){
		System.out.println(e);
	  }
	}
  }

  /**
   * Function which fetches @numConcepts concepts corresponding to the 2 words in @input and finds cosine similarity between each concept vector */
  public void runTask(String[] input, ISearcher searcher, int numConcepts) throws Exception{
	// Get the concepts.
	String word = input[0];

	/* results* contains the top numConcepts articles along with their scores */
	ArrayList<IResult> results1 = searcher.search(word, numConcepts);

	int count = 10;
	for(IResult result: results1){
	  
		 if(count-- >= 0)
		 System.out.println(result.getTitle());
	}
	
  }
}

/**
 * Generates Explicit Semantic Analysis. Uses the Wikipedia index from index-dir
 * and generates the specified number of concepts for the input file.
 *
 * Usage: java ESA index-dir num-concepts file-input file
 *
 * This assumes that descartes-0.2.jar and the other dependencies are in the
 * classpath.
 *
 */
public class ESA {

  public static void main(String[] args) throws Exception {
	if (args.length != 3) {
	  System.err.println("Usage: java ESA index-dir num-concepts file");
	  System.err.println(Arrays.toString(args));
	  System.exit(-1);
	}

	String indexDir = args[0];
	int numConcepts = Integer.parseInt(args[1]);
	String keyword = args[2];

	// Create a new searcher to search the index
	ISearcher searcher = SearcherFactory.getStandardSearcher(indexDir);

	ArrayList<String[]> inputs = new ArrayList();
	String[] data = {keyword};
	inputs.add(data);

	Thread[] threads = new Thread[4];
	for(int i = 0; i < 4; i++) {
	  threads[i] = new Thread(new ParallelESA(inputs, searcher, numConcepts));
	  threads[i].run();
	}
  }
}
