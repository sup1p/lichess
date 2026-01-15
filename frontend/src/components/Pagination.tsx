interface PaginationProps {
  page: number;
  total: number;
  pageSize: number;
  onPrevPage: () => void;
  onNextPage: () => void;
}

export default function Pagination({
  page,
  total,
  pageSize,
  onPrevPage,
  onNextPage,
}: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize);
  const hasNextPage = page < totalPages;
  const hasPrevPage = page > 1;

  return (
    <div className="pagination">
      <button onClick={onPrevPage} disabled={!hasPrevPage}>
        Previous
      </button>
      <div className="pagination-info">
        <span className="pagination-pages">{page} / {totalPages}</span>
        <span className="pagination-total">({total} games)</span>
      </div>
      <button onClick={onNextPage} disabled={!hasNextPage}>
        Next
      </button>
    </div>
  );
}
