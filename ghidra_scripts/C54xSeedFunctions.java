// Finds TMS320C54x code that flow analysis can't reach (handlers reached through computed
// calls) and turns it into functions:
//  1. Names the interrupt handlers in the vector table (default 0x0080: 32 vectors of 4 words,
//     "B handler"); vectors that branch to themselves are left alone.
//  2. Tries every CALL/CALLD target found anywhere in loaded program memory, most referenced
//     first. A target is kept only if disassembling from it raises no errors; otherwise the
//     attempt is rolled back, so data that happens to look like a CALL doesn't become code.
// Script arguments (headless, optional): <vector table word address in hex>
// @category C54x
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class C54xSeedFunctions extends GhidraScript {
    // C5402/C5409/C5416 interrupt numbers by vector slot (device-dependent above slot 18)
    static final String[] VEC = {
        "RS", "NMI", "SINT17", "SINT18", "SINT19", "SINT20", "SINT21", "SINT22", "SINT23", "SINT24",
        "SINT25", "SINT26", "SINT27", "SINT28", "SINT29", "SINT30", "INT0", "INT1", "INT2", "TINT0",
        "BRINT0", "BXINT0", "BRINT2_DMAC0", "BXINT2_DMAC1", "INT3", "HINT", "BRINT1_DMAC2",
        "BXINT1_DMAC3", "DMAC4", "DMAC5", "vec30", "vec31",
    };

    AddressSpace prog;
    Memory mem;

    int word(long a) throws Exception {
        return mem.getShort(prog.getTruncatedAddress(a, true)) & 0xffff;
    }

    boolean loaded(long a) {
        MemoryBlock b = mem.getBlock(prog.getTruncatedAddress(a, true));
        return b != null && b.isInitialized() && b.getStart().getAddressSpace() == prog;
    }

    @Override
    public void run() throws Exception {
        prog = currentProgram.getAddressFactory().getAddressSpace("prog");
        mem = currentProgram.getMemory();
        long vt = getScriptArgs().length > 0 ? Long.parseLong(getScriptArgs()[0], 16) : 0x80;

        int isrs = 0;
        for (int v = 0; v < 32; v++) {
            long slot = vt + 4L * v;
            if (!loaded(slot) || !loaded(slot + 1)) continue;
            int op = word(slot);
            if (op != 0xF073 && op != 0xF273) continue;
            long t = word(slot + 1);
            Address sa = prog.getTruncatedAddress(slot, true);
            createLabel(sa, "VEC_" + VEC[v], true);
            if (t == slot || !loaded(t)) continue;
            Address ta = prog.getTruncatedAddress(t, true);
            disassemble(sa);
            disassemble(ta);
            Function f = getFunctionAt(ta);
            if (f == null) f = createFunction(ta, null);
            if (f != null && f.getName().startsWith("FUN_")) {
                f.setName(v == 0 ? "c_int00" : "isr_" + VEC[v], SourceType.ANALYSIS);
                isrs++;
            }
        }

        // CALL/CALLD targets anywhere in loaded program memory
        Map<Long, Integer> refs = new HashMap<>();
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized() || b.getStart().getAddressSpace() != prog) continue;
            long s = b.getStart().getAddressableWordOffset(), e = b.getEnd().getAddressableWordOffset();
            for (long a = s; a < e; a++) {
                int op = word(a);
                if (op == 0xF074 || op == 0xF274) {
                    long t = word(a + 1);
                    if (loaded(t)) refs.merge(t, 1, Integer::sum);
                }
            }
        }
        List<Long> order = new ArrayList<>(refs.keySet());
        order.sort((x, y) -> refs.get(y) - refs.get(x));

        int kept = 0, rejected = 0;
        for (long t : order) {
            monitor.checkCancelled();
            Address ta = prog.getTruncatedAddress(t, true);
            if (getInstructionContaining(ta) != null) {
                if (getInstructionAt(ta) != null && getFunctionAt(ta) == null && createFunction(ta, null) != null) kept++;
                continue;
            }
            int before = currentProgram.getBookmarkManager().getBookmarkCount("Error");
            DisassembleCommand cmd = new DisassembleCommand(ta, null, true);
            cmd.applyTo(currentProgram, monitor);
            AddressSetView got = cmd.getDisassembledAddressSet();
            if (currentProgram.getBookmarkManager().getBookmarkCount("Error") > before || got.isEmpty()) {
                currentProgram.getListing().clearCodeUnits(got.getMinAddress() == null ? ta : got.getMinAddress(),
                        got.getMaxAddress() == null ? ta : got.getMaxAddress(), false);
                for (var it = currentProgram.getBookmarkManager().getBookmarksIterator("Error"); it.hasNext();) {
                    var bm = it.next();
                    if (got.contains(bm.getAddress()) || bm.getAddress().equals(ta)) currentProgram.getBookmarkManager().removeBookmark(bm);
                }
                rejected++;
                continue;
            }
            if (getFunctionAt(ta) == null && createFunction(ta, null) != null) kept++;
        }
        println(String.format("C54xSeedFunctions: %d interrupt handlers, %d call targets kept, %d rejected", isrs, kept, rejected));
    }
}
